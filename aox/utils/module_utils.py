import importlib.util
import os
from pathlib import Path
from typing import Union, Optional

__all__ = [
    'load_module_from_path',
    'try_import_module',
    'is_import_error_for_own_module',
]

from aox.utils.typing_utils import Module


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


def try_import_module(module_name: str) -> Optional[Module]:
    """
    Try to import a module, and return nothing if it doesn't exit

    >>> try_import_module('aox.utils.non_existing_module')
    >>> try_import_module('aox.utils.module_utils')
    <module ...>
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        if not is_import_error_for_own_module(module_name, e):
            raise

        return None


def is_import_error_for_own_module(
        module_name: str, import_error: ImportError) -> bool:
    """
    Find if an `ImportError` is due to the file not existing, or if it is due to
    some other issue, eg cyclical import.
    """
    parts = module_name.split('.')
    partial_module_names = [
        '.'.join(parts[:last])
        for last in range(1, len(parts) + 1)
    ]
    acceptable_messages = {
        f"No module named '{partial_module_name}'"
        for partial_module_name in partial_module_names
    }
    error_message = getattr(import_error, 'msg')
    return error_message in acceptable_messages
