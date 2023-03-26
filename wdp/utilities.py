import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent


def ensure_in_sys_path(path: os.PathLike | str) -> None:
    """Ensures that the given path is in sys.path."""
    if path not in sys.path:
        sys.path.append(str(path))


def app_root_path() -> pathlib.Path:
    """Returns the project root folder: <git repo root>/wdp/."""
    path = ROOT
    ensure_in_sys_path(path)
    return path


def app_research_path() -> pathlib.Path:
    """Returns the project source folder: <git repo root>/research/."""
    path = ROOT / 'research'
    ensure_in_sys_path(path)
    return path


def app_source_path() -> pathlib.Path:
    """Returns the project source folder: <git repo root>/wdp/."""
    path = ROOT / 'wdp'
    ensure_in_sys_path(path)
    return path


def app_path(folder_name: os.PathLike | str) -> pathlib.Path:
    """Returns the path of the folder with the given name located in app source path."""
    path = app_source_path() / folder_name
    ensure_in_sys_path(path)
    return path
