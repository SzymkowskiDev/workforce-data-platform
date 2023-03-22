"""
wdp.data_converter
~~~~~~~~~~~~~~~~~~
(C) bswck 2023

Parallel data converter from CSV/XLSX to JSON.
Idempotent for the JSON format, but JSON files are recreated anyway to guarantee its compatibility
with the JSON format.

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

    >>> watcher = data_converter.create_watcher(
    ...     callback=callback,
    ...     mode='multiprocessing',  # or 'threading' or 'sync', defaults to 'threading'
    ...     encoding='utf-8',
    ...     recursive=True,
    ... )
    >>> watcher.join()

Thread safety:
    Just don't run this module in multiple processes. It is not fully thread-safe.
"""

from __future__ import annotations
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
import typing

import pandas as pd

from wdp.utilities import app_path

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Literal, SupportsFloat


__all__ = (
    'DataConversionError',
    'DEFAULT_SOURCE_DIRECTORY',
    'DEFAULT_TARGET_DIRECTORY',
    'EXECUTOR_FACTORIES',
    'jsonify_directory',
    'jsonify_file',
    'DirectoryWatcher',
    'create_watcher',
)


logger = logging.getLogger(__name__)

try:
    import orjson as json

    logger.info('using orjson instead of json')
except ImportError:
    import json

    logger.info('orjson unavailable, using json')


_PathLike = os.PathLike | str

_NoFutureReturnT = typing.TypeVar('_NoFutureReturnT')

DEFAULT_SOURCE_DIRECTORY: _PathLike = os.getenv(
    'IO_SOURCE_DIRECTORY', app_path('input_and_output/uploads')
)
DEFAULT_TARGET_DIRECTORY: _PathLike = os.getenv(
    'IO_TARGET_DIRECTORY', app_path('input_and_output/converted')
)
ERROR_LOG_PATH = os.getenv(
    'IO_ERROR_LOG_PATH',
    app_path('input_and_output/error_logs/data_converter.log'),
)


EXECUTOR_FACTORIES: dict[str, type[concurrent.futures.Executor]] = {
    'threading': concurrent.futures.ThreadPoolExecutor,
    'multiprocessing': concurrent.futures.ProcessPoolExecutor,
}


class _NoFuture(typing.Generic[_NoFutureReturnT]):
    """Internal helper for synchronous execution."""

    def __init__(
        self, fn: Callable[[...], _NoFutureReturnT], args: tuple, kwargs: dict
    ):
        self.__fn = fn
        self.__args = args
        self.__kwargs = kwargs

    def result(self) -> _NoFutureReturnT:
        return self.__fn(*self.__args, **self.__kwargs)


class _NoExecutor(concurrent.futures.Executor):
    """Internal helper for synchronous execution."""

    def submit(
        self, fn: Callable[[...], _NoFutureReturnT], /, *args: Any, **kwargs: Any
    ) -> _NoFuture[_NoFutureReturnT]:
        return _NoFuture[_NoFutureReturnT](fn, args, kwargs)


EXECUTOR_FACTORIES['sync'] = _NoExecutor


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


_OnErrorCallbackT = typing.Callable[[io.BufferedReader], typing.Any]


def _try_read_json(
    fp: io.BufferedReader, encoding: str, on_error: _OnErrorCallbackT
) -> dict:
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
) -> pd.DataFrame:
    """Try to read XLSX from a file pointer (stream)."""
    try:
        data = pd.read_excel(fp)
    except Exception:
        data = on_error(fp, encoding)
    return data


def _try_read_csv(
    fp: io.BufferedReader, encoding: str, on_error: _OnErrorCallbackT
) -> pd.DataFrame:
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


def _on_error(fp: io.BufferedReader, encoding: str) -> None:
    """Raise an error when data format could not be guessed."""
    raise DataConversionError('could not guess data format')


_JSON_TOKENS: bytes = b'{['


def jsonify_file(
    path: _PathLike | io.BytesIO,
    encoding: str | None = None,
    on_error: Callable = _on_error,
) -> str | None:
    """Convert file contents into a JSON string."""
    if encoding is None:
        encoding = locale.getpreferredencoding()
    data = None
    if isinstance(path, _PathLike):
        logger.info('Converting file %s to JSON', path)
        try:
            fp = open(path, 'rb')  # pylint: disable=R1732
        except FileNotFoundError as exc:
            raise DataConversionError(f'file not found: {path}') from exc
    else:
        logger.info('Converting file stream to JSON')
        fp = path
    try:
        ch = None
        try:
            while not ch:
                ch = fp.read(1)
                if ch == b"":
                    break
                ch = ch.strip()
        except ValueError:
            pass
        fp.seek(0)
        if ch and ch in _JSON_TOKENS:
            logger.info('File %s is likely a JSON', path)
            data = _try_read_json(
                fp,
                encoding=encoding,
                on_error=lambda fp, encoding: _try_read_csv(
                    fp, encoding=encoding, on_error=on_error
                ),
            )
        else:
            logger.info('File %s is likely a CSV', path)
            data = _try_read_csv(fp, encoding=encoding, on_error=on_error)
        logger.info('File %s has been converted to JSON', path)
    except Exception as exc:
        logger.critical('File %s could not be converted to JSON', path)
        msg = f'{path} ({exc})'
        raise DataConversionError(msg) from exc
    finally:
        logger.info('Closing file %s', path)
        fp.close()
    return _jsonify(data)


_CallbackT = typing.Callable[[dict[str, typing.Any]], typing.Any]


_critical_once = functools.lru_cache(logger.critical)


def default_error_handler(filename: _PathLike):
    """Log errors to a file. LRU cache to avoid duplicate logging."""
    exc, _, _ = sys.exc_info()
    with open(ERROR_LOG_PATH, 'a', encoding=locale.getpreferredencoding()) as log:
        handler, level = logging.StreamHandler(log), logger.getEffectiveLevel()
        logger.addHandler(handler)
        logger.setLevel(logging.CRITICAL)
        _critical_once(f'Error processing {filename}: {exc}', exc_info=True)
        logger.setLevel(level)
        logger.removeHandler(handler)


def jsonify_directory(
    path: _PathLike,
    callback: _CallbackT,
    executor_factory: Callable[[], concurrent.futures.Executor],
    encoding: str | None = None,
    recursive: bool = True,
    error_handler=default_error_handler,
):
    """Convert all files in a directory into JSON strings."""
    logger.info(
        'Handling files from %s%s...', path, ' recursively' if recursive else ''
    )
    futs = {}
    for filename in filter(
        lambda filename: not filename.startswith('.'), os.listdir(path)
    ):
        item_path = os.path.join(path, filename)
        with executor_factory() as executor:
            if os.path.isfile(item_path):
                futs[item_path] = executor.submit(
                    jsonify_file, path=item_path, encoding=encoding
                )
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
                logger.info(
                    'Recursive processing disabled, skipping directory %s', path
                )
                continue
    ret = []
    for filename, fut in futs.items():
        try:
            result = fut.result()
        except DataConversionError:
            error_handler(filename)
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
        source_directory: _PathLike,
        /,
        *,
        encoding: str = os.getenv('IO_ENCODING'),
        callback: Callable[[list[Any]], Any] | None = None,
        jsonifier: Callable[[_PathLike, _CallbackT, ...], list] = jsonify_directory,
        interval: SupportsFloat = 5.0,
        recursive: bool = True,
        executor_factory: concurrent.futures.Executor = concurrent.futures.ThreadPoolExecutor,
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

    def __new__(cls, _, source_directory: _PathLike, /, **_kwargs):
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
        logger.info('Watching directory %s', directory)
        while True:
            with self._mutex:
                data = self.jsonify_directory(
                    directory,
                    callback=self.item_callback,
                    encoding=self.encoding,
                    recursive=self.recursive,
                    executor_factory=self.executor_factory,
                )
            if self.callback:
                self.callback(data)
            time.sleep(self.interval)


def save_converted_json_file(
    target_directory: _PathLike,
    source_directory: _PathLike,
    filename: _PathLike,
    data: _PathLike,
) -> None:
    """Save the JSON string to a file."""
    new_filename = os.path.join(
        os.path.dirname(filename).replace(
            str(source_directory),
            str(target_directory)
        ),
        os.path.basename(filename),
    )
    root_filename, extension = os.path.splitext(new_filename)
    os.makedirs(os.path.dirname(root_filename), exist_ok=True)
    target_filename = '.'.join((root_filename, extension.lstrip('.'), 'json'))
    logger.info('Saving converted file %s to %s', filename, target_filename)
    with open(target_filename, 'w', encoding=locale.getpreferredencoding()) as fp:
        fp.write(data)


def create_watcher(
    source_directory: _PathLike,
    target_directory: _PathLike,
    mode: Literal['threading', 'multiprocessing', 'sync'] = 'threading',
    watcher_cls: type[DirectoryWatcher] = DirectoryWatcher,
    **kwds,
) -> DirectoryWatcher:
    """Convenience function to run a directory watcher in a thread."""
    if mode and not kwds.get('executor_factory'):
        kwds['executor_factory'] = EXECUTOR_FACTORIES[mode]
    thread = watcher_cls(
        functools.partial(save_converted_json_file, target_directory, source_directory),
        source_directory,
        **kwds,
    )
    return thread


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.INFO)
    watcher_thread = create_watcher(
        app_path('input_and_output/uploads'),
        app_path('input_and_output/converted'),
        mode='sync',
    )
    watcher_thread.start()
    watcher_thread.join()
