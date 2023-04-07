"""
wdp.data_converter
~~~~~~~~~~~~~~~~~~
(C) bswck 2023

This module contains the functions to convert data from CSV, Excel and JSON format to JSON.

To convert a file (stream), use the :function:`convert_file()` function (pass in a file name or the stream).
To convert all files in a directory, optionally recursively, use the :function:`jsonify()` function and pass in a path.
To create a background thread to convert files with a given interval, use the :function:`directory_watcher()` function.
"""

import functools
import io
import json
import locale
import logging
import os
import pathlib
import threading
import time
import typing
from typing import Any, SupportsFloat
from queue import Queue, Empty

import pandas as pd
import csv

from wdp.utilities import app_path


MAGIC_EXCEL: bytes = b'PK'
DEFAULT_ENCODING: str = os.getenv('DATA_ENCODING', locale.getpreferredencoding())
DATA_SOURCE_DIRECTORY: pathlib.Path = pathlib.Path(
    os.getenv('DATA_SOURCE_DIRECTORY', app_path('input_and_output/uploads/'))
)
DATA_TARGET_DIRECTORY: pathlib.Path = pathlib.Path(
    os.getenv('DATA_TARGET_DIRECTORY', app_path('input_and_output/converted/'))
)

logger = logging.getLogger(__name__)
_logger_exception_once = functools.lru_cache(logger.exception)


class CorruptFileError(Exception):
    """Exception raised for corrupt files."""

    @classmethod
    def reraise(cls, *exceptions) -> typing.Callable:
        """Reraise selected exception as CorruptFileError."""
        exceptions = exceptions or Exception

        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    raise cls(e) from e
            return wrapper

        return decorator


def convert_file(
        filename_or_buf: os.PathLike | str | typing.BinaryIO,
        encoding: str = DEFAULT_ENCODING,
) -> str:
    """Convert file's contents into JSON format and return it."""
    if isinstance(filename_or_buf, os.PathLike | str):
        assert os.path.isfile(filename_or_buf)
        if not os.path.isabs(filename_or_buf):
            filename_or_buf = DATA_SOURCE_DIRECTORY / filename_or_buf
        data = io.BytesIO(pathlib.Path(filename_or_buf).read_bytes())
    else:
        data = filename_or_buf
    return convert_data(data, encoding)


@CorruptFileError.reraise(UnicodeDecodeError)
def convert_data(
        buf: typing.BinaryIO,
        encoding: str = DEFAULT_ENCODING,
) -> str:
    """Read a byte buffer and return the data in the JSON format."""
    ch = buf.read(2)
    buf.seek(0)
    if ch != MAGIC_EXCEL:
        arr = buf.read()
        string = arr.decode(encoding)
        if ch and ch[0] in b'{[':
            data = read_json(string)
        else:
            data = read_csv(string)
    else:
        data = read_xlsx(buf.read())
    json_data = dump_data(data)
    return json_data


@CorruptFileError.reraise(csv.Error, pd.errors.ParserError)
def read_csv(data: str) -> str:
    """Reads a CSV file."""
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(data)
    return pd.read_csv(io.StringIO(data), dialect=dialect)  # type: ignore


@CorruptFileError.reraise(json.JSONDecodeError)
def read_json(data: str) -> dict:
    """Reads a JSON file."""
    return json.loads(data)


@CorruptFileError.reraise(pd.errors.ParserError)
def read_xlsx(data: bytes) -> pd.DataFrame:
    """Reads an Excel file."""
    return pd.read_excel(io.BytesIO(data))


@functools.singledispatch
def dump_data(_data_object: Any) -> str:
    """Formats a string."""
    raise NotImplementedError


@dump_data.register
def format_dict(data: dict) -> str:
    """Formats a JSON string."""
    return json.dumps(data)


@dump_data.register
def format_dataframe(data: pd.DataFrame) -> str:
    """Formats a JSON string."""
    return pd.io.json.dumps(data.to_dict(orient='list'), indent=2)


def jsonify_directory(
        directory: os.PathLike | str,
        encoding: str = DEFAULT_ENCODING,
        recursive: bool = False,
) -> None:
    """Walks through a directory and converts all files to JSON."""
    if not os.path.isabs(directory):
        directory = DATA_SOURCE_DIRECTORY / directory
    for root, _, files in os.walk(directory):
        if not recursive:
            if root != directory:
                continue
        for file in files:
            jsonify(os.path.join(root, file), encoding)


def jsonify(
        path: os.PathLike | str,
        encoding: str = DEFAULT_ENCODING,
        recursive: bool = False,
        allow_directory: bool = True,
) -> None:
    """Converts a file to JSON."""
    if not os.path.isabs(path):
        path = DATA_SOURCE_DIRECTORY / path
    path = pathlib.Path(path)
    if path.is_file():
        json_data = None
        with open(path, 'rb') as file:
            try:
                json_data = convert_file(file, encoding)
            except CorruptFileError:
                _logger_exception_once('Error processing file %s', path)
        if json_data is not None:
            new_path = f'{str(path).replace(str(DATA_SOURCE_DIRECTORY), str(DATA_TARGET_DIRECTORY))}.json'
            with open(new_path, 'wb') as file:
                file.write(json_data.encode(encoding))
    else:
        if not allow_directory:
            raise ValueError(f'{path!r} is not a file.')
        jsonify_directory(path, encoding, recursive=recursive)


class QueueConverter(threading.Thread):
    """Creates a thread for converting files to JSON."""
    def __init__(
            self,
            queue: Queue | None = None,
            interval: SupportsFloat = 1,
    ):
        super().__init__()
        self.queue = queue or Queue()
        self.interval = float(interval)

    def run(self):
        while True:
            try:
                path = self.queue.get(block=False)
                if path is None:
                    break
            except Empty:
                logger.debug('Queue is empty, no action taken.')
            else:
                jsonify(path, allow_directory=False)
            time.sleep(self.interval)

    def stop(self):
        self.queue.put(None)


class FileWatcher(Queue):
    """Creates a thread for watching a directory."""

    def __init__(
            self,
            directory: os.PathLike | str,
            recursive: bool = False,
    ):
        super().__init__()
        self.queue = set()
        self.directory = directory
        self.recursive = recursive

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

    def update(self):
        for root, _, files in os.walk(self.directory):
            if not self.recursive and root != str(self.directory):
                continue
            for file in files:
                path = os.path.join(root, file)
                if os.path.isfile(path):
                    super().put(path, block=False)

    def get(self, block: bool = True, timeout: float | None = None):
        self.update()
        return super().get(block, timeout)

    def put(self, *args, **kwargs):
        raise ValueError('Cannot put items into a FileWatcher.')


def directory_converter(
        directory: os.PathLike | str = DATA_SOURCE_DIRECTORY,
        recursive: bool = False,
        interval: SupportsFloat = 1,
) -> QueueConverter:
    """Creates a thread for watching a directory."""
    watcher = FileWatcher(directory, recursive)
    converter = QueueConverter(watcher, interval)
    return converter


if __name__ == '__main__':
    conv = directory_converter()
    conv.start()
