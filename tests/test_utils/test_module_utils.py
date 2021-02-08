import importlib
from unittest import TestCase

from aox.utils import load_module_from_path, get_current_directory, \
    is_import_error_for_own_module, try_import_module

current_directory = get_current_directory()


class TestLoadModuleFromPath(TestCase):
    def test_can_load_non_reachable_module(self):
        non_reachable_module_path = current_directory\
            .joinpath('.non-python.reachable-directory')\
            .joinpath('non.reachable.mod-ule.py')
        module = load_module_from_path(non_reachable_module_path)
        self.assertIsNotNone(module)
        self.assertEqual(module.VALUE, "success")

    def test_can_load_reachable_module(self):
        module = load_module_from_path(__file__)
        self.assertIsNotNone(module)
        # Loading this way does not re-use an existing loaded module
        self.assertNotEqual(
            module.TestLoadModuleFromPath, TestLoadModuleFromPath)

    def test_module_is_separately_loaded(self):
        module_a = load_module_from_path(__file__)
        module_b = load_module_from_path(__file__)
        self.assertNotEqual(module_a, module_b)
        self.assertNotEqual(
            module_a.TestLoadModuleFromPath, module_b.TestLoadModuleFromPath)


class TestTryImportModule(TestCase):
    def test_import_existing_module(self):
        module = try_import_module(
            'tests.test_utils.modules_for_test.normal_module')
        self.assertIsNotNone(module)
        self.assertEqual(module.VALUE, 1)

    def test_import_missing_module(self):
        module = try_import_module(
            'tests.test_utils.modules_for_test.missing_module')
        self.assertIsNone(module)

    def test_import_module_with_error(self):
        with self.assertRaises(ZeroDivisionError):
            try_import_module(
                'tests.test_utils.modules_for_test.module_with_error')

    def test_import_module_with_cyclical_imports(self):
        with self.assertRaises(AttributeError):
            try_import_module(
                'tests.test_utils.modules_for_test.cyclic_import_a')


class TestIsImportErrorForOwnModule(TestCase):
    def get_import_error(self, module_name):
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            return e

    def is_import_error_for_own_module(self, module_name):
        return is_import_error_for_own_module(
            module_name, self.get_import_error(module_name))

    def test_completely_missing_module_is_own_import_error(self):
        self.assertIsNotNone(self.get_import_error(
            'not_existing'))
        self.assertTrue(self.is_import_error_for_own_module(
            'not_existing.package.guaranteed'))

    def test_partially_missing_module_is_own_import_error(self):
        self.assertIsNone(self.get_import_error(
            'tests.test_utils.modules_for_test'))
        self.assertTrue(self.is_import_error_for_own_module(
            'tests.test_utils.modules_for_test.not_existing.module'))
