from unittest import TestCase
from unittest.mock import patch

from aox.controller.controller import Controller
from aox.settings import settings_proxy
from tests.utils import preparing_to_init_settings


class TestControllerInitSettings(TestCase):
    def test_init_settings_with_no_settings(self):
        with preparing_to_init_settings() as settings_directory:
            self.assertTrue(Controller().init_settings())
            self.assertTrue(settings_proxy.has())
            self.assertTrue(settings_proxy().path.exists())
            self.assertTrue(
                settings_proxy().path.is_relative_to(settings_directory))

    def test_init_settings_with_existing_settings_doesnt_recreate_it(self):
        with preparing_to_init_settings() as settings_directory:
            Controller().init_settings()
            existing_settings = settings_proxy()
            with patch.object(Controller, 'create_settings') \
                    as create_settings_mock:
                self.assertFalse(Controller().init_settings())
            self.assertTrue(settings_proxy.has())
            self.assertTrue(settings_proxy().path.exists())
            self.assertTrue(
                settings_proxy().path.is_relative_to(settings_directory))
            self.assertEqual(settings_proxy(), existing_settings)
            self.assertEqual(create_settings_mock.call_count, 0)
