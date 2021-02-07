from unittest import TestCase

from aox.settings import Settings
from tests.utils import DummyModule


class TestAccessingExtraSettings(TestCase):
    def test_can_add_unknown_settings(self):
        Settings.from_settings_module(
            DummyModule(UNKNOWN_SETTING="foo"), None, None, None)

    def test_can_access_unknown_settings(self):
        settings = Settings.from_settings_module(
            DummyModule(UNKNOWN_SETTING="foo"), None, None, None)
        self.assertEqual(settings.module.UNKNOWN_SETTING, "foo")

    def test_can_unknown_settings_are_not_accessible_from_settings(self):
        settings = Settings.from_settings_module(
            DummyModule(UNKNOWN_SETTING="foo"), None, None, None)
        self.assertFalse(hasattr(settings, 'UNKNOWN_SETTING'))
        self.assertFalse(hasattr(settings, 'unknown_setting'))

    def test_can_known_settings_are_accessible_from_settings(self):
        settings = Settings.from_settings_module(
            DummyModule(CHALLENGES_MODULE_NAME_ROOT="bar"), None, None, None)
        self.assertEqual(settings.challenges_module_name_root, "bar")

    def test_can_access_known_settings(self):
        settings = Settings.from_settings_module(
            DummyModule(CHALLENGES_MODULE_NAME_ROOT="bar"), None, None, None)
        self.assertEqual(settings.module.CHALLENGES_MODULE_NAME_ROOT, "bar")
