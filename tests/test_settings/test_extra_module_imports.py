import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase

from aox.settings import Settings
from aox.utils import get_current_directory
from tests.test_settings.dummy_registry import dummy_registry
from tests.utils import resetting_modules

current_directory = get_current_directory()
example_dummy_registrant_contents = current_directory\
    .joinpath('example_dummy_registrant.py')\
    .read_bytes()


class DummyModule:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestExtraModuleImports(TestCase):
    @contextmanager
    def creating_dummy_module(self):
        dummy_registry.clear()
        with tempfile.NamedTemporaryFile(
                dir=current_directory, suffix=".py") as f_dummy:
            dummy_module_name, _ = os.path.splitext(Path(f_dummy.name).name)
            parent_module_name, _ = __name__.rsplit('.', 1)
            full_dummy_module_name = f"{parent_module_name}.{dummy_module_name}"
            f_dummy.write(example_dummy_registrant_contents.replace(
                b"MODULE_NAME", f"From {full_dummy_module_name}".encode()))
            f_dummy.flush()
            with resetting_modules(f_dummy.name):
                try:
                    yield full_dummy_module_name
                finally:
                    dummy_registry.clear()

    def test_default_import_list_doesnt_raise(self):
        Settings.from_settings_module(DummyModule(), None, None, None)

    def test_empty_import_list_doesnt_raise(self):
        Settings.from_settings_module(DummyModule(), None, None, None)

    def test_existing_extra_import_is_imported(self):
        with self.creating_dummy_module() as full_dummy_module_name:
            Settings.from_settings_module(DummyModule(
                EXTRA_MODULE_IMPORTS=[full_dummy_module_name],
            ), None, None, None)
            self.assertEqual(
                dummy_registry, {"dummy": f"From {full_dummy_module_name}"})

    def test_non_existing_extra_import_raises(self):
        with self.assertRaises(ModuleNotFoundError):
            Settings.from_settings_module(DummyModule(
                EXTRA_MODULE_IMPORTS=["tests.test_settings.not_existing"],
            ), None, None, None)
        self.assertEqual(dummy_registry, {})
