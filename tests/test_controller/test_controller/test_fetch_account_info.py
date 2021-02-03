import json
from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch

from aox.controller.controller import Controller
from aox.model import AccountInfo
from aox.settings import settings_proxy
from tests.utils import preparing_to_init_settings


# noinspection DuplicatedCode
class TestControllerFetchAccountInfo(TestCase):
    @contextmanager
    def preparing_to_fetch_info(self, account_info):
        with preparing_to_init_settings():
            controller = Controller()
            controller.init_settings()
            with patch.object(AccountInfo, 'from_site',
                              return_value=account_info):
                yield controller

    @contextmanager
    def fetching_info(self, account_info, expected_result):
        with self.preparing_to_fetch_info(account_info) as controller:
            self.assertEqual(controller.fetch_account_info(), expected_result)
            yield controller

    def test_fetching_empty_account_info_doesnt_change_combined_info_and_cached_data(self):
        with self.preparing_to_fetch_info(None) as controller:
            combined_info = controller.combined_info
            self.assertFalse(controller.fetch_account_info())
            self.assertEqual(
                settings_proxy().site_data_path.read_text(), "null\n")
        self.assertEqual(controller.combined_info, combined_info)

    def test_fetching_account_info_changes_cached_data(self):
        account_info = AccountInfo.from_collected_data({
            "username": "Test User", "total_stars": 3, "years": {
                2020: {"year": 2020, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        })
        with self.fetching_info(account_info, True) as controller:
            self.assertEqual(
                json.loads(settings_proxy().site_data_path.read_text()),
                account_info.serialise())
        self.assertTrue(
            controller.combined_info.get_part(2020, 2, 'a').has_star)
        self.assertFalse(
            controller.combined_info.get_part(2020, 3, 'a').has_star)

    def test_fetching_account_info_writes_to_missing_cache(self):
        account_info = AccountInfo.from_collected_data({
            "username": "Test User", "total_stars": 3, "years": {
                2020: {"year": 2020, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        })
        with self.preparing_to_fetch_info(account_info) as controller:
            site_data_path = settings_proxy().site_data_path
            site_data_path.unlink()
            self.assertTrue(controller.fetch_account_info())
            self.assertTrue(site_data_path.exists())
            self.assertEqual(
                json.loads(site_data_path.read_text()),
                account_info.serialise())
        self.assertTrue(
            controller.combined_info.get_part(2020, 2, 'a').has_star)
        self.assertFalse(
            controller.combined_info.get_part(2020, 3, 'a').has_star)
