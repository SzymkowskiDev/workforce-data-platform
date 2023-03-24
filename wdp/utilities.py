import os
import pathlib
from typing import Callable, TypeVar, Any

ROOT = pathlib.Path(__file__).parent


def app_root_path() -> pathlib.Path:
    """Returns the project root folder: <git repo root>/wdp/."""
    return ROOT


def app_path(folder_name: os.PathLike | str) -> pathlib.Path:
    """Returns the path of the folder with the given name."""
    return app_root_path() / folder_name
