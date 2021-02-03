from unittest import TestCase
from unittest.mock import patch

from aox.web import WebAoc
from tests.utils import using_controller


class TestControllerRefreshChallengeInput(TestCase):
    def check_challenge_input(
            self, parts_to_create_on_disk, collected_data,
            year, day, only_if_empty,
            remote_input, initial_content, expected_content, expected_result):
        with using_controller(parts_to_create_on_disk, collected_data) \
                as (controller, combined_info, _), \
                patch.object(WebAoc, 'get_input_page',
                             return_value=remote_input):
            challenge_input_path = combined_info\
                .get_day(year, day).get_input_filename()
            if initial_content is not None:
                challenge_input_path.write_text(initial_content)
            self.assertEqual(controller.refresh_challenge_input(
                year, day, only_if_empty=only_if_empty), expected_result)
            if challenge_input_path.exists():
                content = challenge_input_path.read_text()
            else:
                content = None

            self.assertEqual(content, expected_content)

    def test_original_empty_doesnt_change_with_failed_response(self):
        self.check_challenge_input(
            [(2020, 1, 'a')], None, 2020, 1, True,
            None, None, '', False)

    def test_original_empty_changes_with_successful_response(self):
        self.check_challenge_input(
            [(2020, 1, 'a')], None, 2020, 1, True,
            "Test Input", None, "Test Input", True)

    def test_original_not_empty_does_not_change_with_only_if_empty(self):
        self.check_challenge_input(
            [(2020, 1, 'a')], None, 2020, 1, True,
            "Test Input", "Something else", "Something else", False)

    def test_original_not_empty_changes_with_without_only_if_empty(self):
        self.check_challenge_input(
            [(2020, 1, 'a')], None, 2020, 1, False,
            "Test Input", "Something else", "Test Input", True)
