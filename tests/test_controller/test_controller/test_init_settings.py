from unittest import TestCase
from unittest.mock import patch

from aox.controller.controller import Controller
from aox.settings import has_settings, get_settings
from tests.utils import preparing_to_init_settings


class TestControllerInitSettings(TestCase):
    def test_init_settings_with_no_settings(self):
        with preparing_to_init_settings() as settings_directory:
            self.assertTrue(Controller().init_settings())
            self.assertTrue(has_settings())
            self.assertTrue(get_settings().path.exists())
            self.assertTrue(
                get_settings().path.is_relative_to(settings_directory))

    def test_init_settings_with_existing_settings_doesnt_recreate_it(self):
        with preparing_to_init_settings() as settings_directory:
            Controller().init_settings()
            existing_settings = get_settings()
            with patch.object(Controller, 'create_settings') \
                    as create_settings_mock:
                self.assertFalse(Controller().init_settings())
            self.assertTrue(has_settings())
            self.assertTrue(get_settings().path.exists())
            self.assertTrue(
                get_settings().path.is_relative_to(settings_directory))
            self.assertEqual(get_settings(), existing_settings)
            self.assertEqual(create_settings_mock.call_count, 0)
