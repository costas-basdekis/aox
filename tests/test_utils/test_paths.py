from unittest import TestCase

from aox.utils import paths

current_directory = paths.get_current_directory()


class TestLoadModuleFromPath(TestCase):
    def test_can_load_non_reachable_module(self):
        non_reachable_module_path = current_directory\
            .joinpath('.non-python.reachable-directory')\
            .joinpath('non.reachable.mod-ule.py')
        module = paths.load_module_from_path(non_reachable_module_path)
        self.assertIsNotNone(module)
        self.assertEqual(module.VALUE, "success")

    def test_can_load_reachable_module(self):
        module = paths.load_module_from_path(__file__)
        self.assertIsNotNone(module)
        # Loading this way does not re-use an existing loaded module
        self.assertNotEqual(
            module.TestLoadModuleFromPath, TestLoadModuleFromPath)

    def test_module_is_separately_loaded(self):
        module_a = paths.load_module_from_path(__file__)
        module_b = paths.load_module_from_path(__file__)
        self.assertNotEqual(module_a, module_b)
        self.assertNotEqual(
            module_a.TestLoadModuleFromPath, module_b.TestLoadModuleFromPath)
