import importlib.util
import inspect
import os
from pathlib import Path


__all__ = [
    'get_caller_file_name',
    'get_current_directory',
    'load_module_from_path',
]

from typing import Union


def get_caller_file_name(skip_frames=1):
    """
    Get the file name of the original caller of the calling function.

    :param skip_frames: The number of frames to skip to get the caller. If you
    want your filename, set to 0, if you want your caller's leave to default or
    set to 1, and any number above that to traverse your callers.

    >>> get_caller_file_name(0)
    '.../utils/paths.py'
    >>> def example_caller():
    ...     return get_caller_file_name()
    >>> example_caller()
    '.../utils/paths.py'
    """
    caller = inspect.stack()[1 + skip_frames]
    caller_frame, *_ = caller
    caller_globals = caller_frame.f_globals
    module_file_name = caller_globals.get('__file__', None)

    return module_file_name


def get_root_directory():
    """
    Get the root directory of this repo

    >>> import sys
    >>> if sys.version_info >= (3, 9):
    ...     get_current_directory().is_relative_to(get_root_directory())
    ... else:
    ...     True
    True
    >>> if sys.version_info >= (3, 9):
    ...     str(get_current_directory().relative_to(get_root_directory()))
    ... else:
    ...     'aox/utils'
    'aox/utils'
    """
    return Path('.').absolute()


def get_current_directory(module_file_name=None):
    """
    Get the directory of the module where this is called from. Usually called as
    `get_current_directory()`, or `get_current_directory(__file__)`.

    >>> str(get_current_directory())
    '.../utils'
    """
    if module_file_name is None:
        module_file_name = get_caller_file_name()
        if not module_file_name:
            raise Exception(
                f"Could not get the file name of the calling module "
                f"automatically - call with `__file__` as the only parameter, "
                f"or specify the file name explicitly.")
    return Path(os.path.dirname(os.path.realpath(module_file_name)))


def load_module_from_path(path: Union[Path, str], module_name: str = None):
    """
    Load a module only by it's given path. This is useful when you want to load
    a single Python module from a path that either isn't in the `PYTHONPATH`, or
    isn't a valid Python path.

    Currently used for loading sensitive user settings in
    `.aox/sensitive_user_settings.py`.

    :param path: The full path to the module
    :param module_name: The name to give to the loaded module. By default it
    uses the filename
    :return:
    """
    if isinstance(path, str):
        path = Path(path)
    if module_name is None:
        module_name, _ = os.path.splitext(path.name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    # noinspection PyUnresolvedReferences
    spec.loader.exec_module(module)

    return module
