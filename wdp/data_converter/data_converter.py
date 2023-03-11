"""
wdp.data_converter
~~~~~~~~~~~~~~~~~~
(C) bswck 2023

Parallel data converter from CSV/XLSX to JSON.
Idempotent for the JSON format, but JSON files are recreated anyway to guarantee complying to
the format.

This module provides functions to convert CSV/XLSX files to JSON in parallel.
It also provides a class DirectoryWatcher to watch a directory for new files and convert them
to JSON in parallel in a background thread.

Example usage of programmatical conversion:
    >>> from wdp import data_converter

    >>> def callback(filename, data):
    ...     print(f'Converted {filename} to JSON')

    >>> data_converter.jsonify_directory(
    ...     path='path/to/directory',
    ...     callback=callback,
    ...     executor_factory=data_converter.EXECUTOR_FACTORIES['threading'],
    ...     encoding='utf-8',
    ...     recursive=False,
    ... )

Example usage of directory watcher:
    >>> from wdp import data_converter

    >>> watcher = data_converter.run_watcher(
    ...     callback=callback,
    ...     mode='multiprocessing',  # or 'threading' or 'sync', defaults to 'threading'
    ...     encoding='utf-8',
    ...     recursive=True,
    ... )
    >>> watcher.join()

Thread safety:
    Just don't run this module in multiple processes. It is not fully thread-safe.
"""


import concurrent.futures
import csv
import functools
import io
import locale
import logging
import os
import sys
import threading
import time
import pandas as pd

from typing import Any, Callable, Literal, SupportsFloat


__all__ = (
    'DataConversionError',
    'DEFAULT_SOURCE_DIRECTORY',
    'DEFAULT_TARGET_DIRECTORY',
    'EXECUTOR_FACTORIES',
    'jsonify_directory',
    'jsonify_file',
    'DirectoryWatcher',
    'run_watcher'
)


logger = logging.getLogger(__name__)

try:
    import orjson as json
    logger.info('using orjson instead of json')
except ImportError:
    import json
    logger.info('orjson unavailable, using json')


class _NoFuture:
    """Internal helper for synchronous execution."""
    def __init__(self, fn, args, kwargs):
        self.__fn = fn
        self.__args = args
        self.__kwargs = kwargs

    def result(self):
        return self.__fn(*self.__args, **self.__kwargs)


class _NoExecutor(concurrent.futures.Executor):
    """Internal helper for synchronous execution."""
    def submit(self, fn, *args, **kwargs):
        return _NoFuture(fn, args, kwargs)


EXECUTOR_FACTORIES = {
    'threading': concurrent.futures.ThreadPoolExecutor,
    'multiprocessing': concurrent.futures.ProcessPoolExecutor,
    'sync': _NoExecutor,
}

__local_path = functools.partial(os.path.join, os.path.dirname(__file__))
DEFAULT_SOURCE_DIRECTORY = os.getenv(
    'IO_SOURCE_DIRECTORY', __local_path('../input_and_output/uploads')
)
DEFAULT_TARGET_DIRECTORY = os.getenv(
    'IO_TARGET_DIRECTORY', __local_path('../input_and_output/converted')
)
ERROR_LOG_PATH = os.getenv(
    'IO_ERROR_LOG_PATH', __local_path('../input_and_output/error.log')
)
_JSON_TOKENS = b'{['


class DataConversionError(Exception):
    """Raised when data conversion fails."""


@functools.singledispatch
def _jsonify(data: Any) -> Any:
    """Convert data to JSON."""
    return json.dumps(data)


@_jsonify.register
def _jsonify_df(data: pd.DataFrame) -> str:
    """Convert a DataFrame to JSON."""
    return pd.io.json.dumps(
        data.to_dict(orient='list'),
        indent=2,
    )


_OnErrorCallbackT = Callable[[io.BufferedReader], Any]


def _try_read_json(
        fp: io.BufferedReader,
        encoding: str,
        on_error: _OnErrorCallbackT
):
    """Try to read JSON from a file pointer (stream)."""
    try:
        data = json.loads(fp.read().decode(encoding)).dumps()
    except ValueError:
        data = on_error(fp, encoding)
    return data


def _try_read_xlsx(
        fp: io.BufferedReader,
        encoding: str,
        on_error: _OnErrorCallbackT,
):
    """Try to read XLSX from a file pointer (stream)."""
    try:
        data = pd.read_excel(fp)
    except Exception:
        data = on_error(fp, encoding)
    return data


def _try_read_csv(
        fp: io.BufferedReader,
        encoding: str,
        on_error: _OnErrorCallbackT
):
    """Try to read CSV from a file pointer (stream)."""
    buf = fp.read()
    try:
        data = buf.decode(encoding)
    except ValueError:
        # probably some weird binary data file, check for xlsx
        data = None
    if data is None:
        fp.seek(0)
        return _try_read_xlsx(fp, encoding, on_error)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(data)
    except csv.Error:
        return on_error(fp, encoding)
    return pd.read_csv(io.StringIO(data), dialect=dialect)


def _on_error(fp: io.BufferedReader, encoding: str):
    """Raise an error when data format could not be guessed."""
    raise DataConversionError('could not guess data format')


def jsonify_file(
        path: str | io.BytesIO,
        encoding: str | None = None,
        on_error: Callable = _on_error
) -> str | None:
    """Convert file contents into a JSON string."""
    if encoding is None:
        encoding = locale.getpreferredencoding()
    data = None
    if isinstance(path, str):
        logger.info(f'Converting file {path} to JSON')
        try:
            fp = open(path, 'rb')
        except FileNotFoundError as exc:
            raise DataConversionError(f'file not found: {path}') from exc
    else:
        logger.info(f'Converting file stream to JSON')
        fp = path
    try:
        ch = None
        try:
            while not ch:
                ch = fp.read(1)
                if ch == b'':
                    break
                ch = ch.strip()
        except ValueError:
            pass
        fp.seek(0)
        if ch and ch in _JSON_TOKENS:
            logger.info(f'File {path} is likely a JSON')
            data = _try_read_json(
                fp, encoding=encoding,
                on_error=lambda fp, encoding: _try_read_csv(
                    fp, encoding=encoding,
                    on_error=on_error
                ),
            )
        else:
            logger.info(f'File {path} is likely a CSV')
            data = _try_read_csv(fp, encoding=encoding, on_error=on_error)
        logger.info(f'File {path} has been converted to JSON')
    except Exception as e:
        logger.critical(f'File {path} could not be converted to JSON')
        msg = f'{path} ({e})'
        raise DataConversionError(msg) from e
    finally:
        logger.info(f'Closing file {path}')
        fp.close()
    return _jsonify(data)


_CallbackT = Callable[[dict[str, Any]], Any]


@functools.lru_cache()
def default_error_handler(filename, exc):
    """Log errors to a file. LRU cache to avoid duplicate logging."""
    with open(ERROR_LOG_PATH, 'a') as log:
        handler, level = logging.StreamHandler(log), logger.getEffectiveLevel()
        logger.addHandler(handler)
        logger.setLevel(logging.CRITICAL)
        logger.critical(f'Error processing {filename}: {exc}', exc_info=True)
        logger.setLevel(level)
        logger.removeHandler(handler)


def jsonify_directory(
        path: str,
        callback: _CallbackT,
        executor_factory: Callable[[], concurrent.futures.Executor],
        encoding: str | None = None,
        recursive: bool = True,
        error_handler=default_error_handler,
):
    """Convert all files in a directory into JSON strings."""
    logger.info(f'Handling files from {path} recursively...')
    futs = {}
    for filename in filter(lambda filename: not filename.startswith('.'), os.listdir(path)):
        item_path = os.path.join(path, filename)
        with executor_factory() as executor:
            if os.path.isfile(item_path):
                futs[item_path] = executor.submit(jsonify_file, path=item_path, encoding=encoding)
            elif recursive:
                futs[item_path] = executor.submit(
                    jsonify_directory,
                    encoding=encoding,
                    path=item_path,
                    callback=callback,
                    recursive=recursive,
                    executor_factory=executor_factory,
                )
                continue
            else:
                logger.info(f'Recursive processing disabled, skipping directory {item_path}')
                continue
    ret = []
    for filename, fut in futs.items():
        try:
            result = fut.result()
        except DataConversionError as exc:
            # normally would use sys.exc_info() inside the callee,
            # but this allows LRU cache to do the right thing
            error_handler(filename, exc)
            continue
        callback(filename, result)
        ret.append(result)
    return ret


class DirectoryWatcher(threading.Thread):
    _mutex = threading.RLock()
    _registry = {}

    def __init__(
            self,
            item_callback: _CallbackT,
            source_directory: str, *,
            encoding: str = os.getenv('IO_ENCODING'),
            callback: Callable[[list[Any]], Any] | None = None,
            jsonifier=jsonify_directory,
            interval: SupportsFloat = 5.0,
            recursive: bool = True,
            executor_factory: concurrent.futures.Executor = concurrent.futures.ThreadPoolExecutor
    ):
        super().__init__()
        self.item_callback = item_callback
        self.encoding = encoding
        self.jsonify_directory = jsonifier
        self.interval = interval
        self.callback = callback
        self.watch_directory = source_directory
        self.recursive = recursive
        self.executor_factory = executor_factory

    def __new__(cls, item_callback, source_directory, **kwargs):
        """Use singleton pattern to avoid multiple watchers for the same directory."""
        normalized_path = os.path.normpath(source_directory)
        if cls._registry.get(normalized_path):
            raise ValueError(f'watcher for {normalized_path} already exists')
        watcher = super().__new__(cls)
        cls._registry[normalized_path] = watcher
        return watcher

    def __del__(self):
        """Remove the watcher from the registry."""
        normalized_path = os.path.normpath(self.watch_directory)
        self._registry.pop(normalized_path, None)

    def run(self):
        """Watch the directory for changes and convert files to JSON."""
        directory = self.watch_directory
        logger.info(f'Watching directory {directory}')
        while True:
            with self._mutex:
                data = self.jsonify_directory(
                    directory,
                    callback=self.item_callback,
                    encoding=self.encoding,
                    recursive=self.recursive,
                    executor_factory=self.executor_factory
                )
            self.callback and self.callback(data)
            time.sleep(self.interval)


def save_converted_json_file(
    target_directory: str, source_directory: str, filename: str, data: str
) -> None:
    """Save the JSON string to a file."""
    new_filename = os.path.join(
        os.path.dirname(filename).replace(source_directory, target_directory),
        os.path.basename(filename)
    )
    root_filename, extension = os.path.splitext(new_filename)
    os.makedirs(os.path.dirname(root_filename), exist_ok=True)
    target_filename = '.'.join((root_filename, extension.lstrip('.'), 'json'))
    logger.info(f'Saving converted file {filename} to {target_filename}')
    with open(target_filename, 'w') as fp:
        fp.write(data)


def run_watcher(
        source_directory: str,
        target_directory: str,
        mode: Literal['threading', 'multiprocessing', 'sync'] = 'threading',
        watcher_cls: type[DirectoryWatcher] = DirectoryWatcher,
        **kwds,
) -> DirectoryWatcher:
    """Convenience function to run a directory watcher in a thread."""
    if mode and not kwds.get('executor_factory'):
        kwds['executor_factory'] = EXECUTOR_FACTORIES[mode]
    kwds['source_directory'] = source_directory
    kwds.setdefault(
        'item_callback', functools.partial(
            save_converted_json_file,
            target_directory,
            source_directory
        )
    )
    thread = watcher_cls(**kwds)
    thread.start()
    return thread


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.INFO)
    thread = run_watcher(
        r'../input_and_output/uploads',
        r'../input_and_output/converted',
    )
    thread.join()
