from contextlib import contextmanager
from unittest import TestCase

from tests.test_controller.test_controller.test_boilerplate import \
    DummyBoilerplate
from tests.utils import using_controller, amending_settings


class TestControllerAddChallenge(TestCase):
    @contextmanager
    def checking_add_challenge(self, year, day, part, expected_result):
        with using_controller([], None) as (controller, combined_info, _), \
                amending_settings(challenges_boilerplate=DummyBoilerplate()):
            expected_contents = {}
            yield controller, combined_info, expected_contents
            self.assertEqual(controller.add_challenge(
                year, day, part), expected_result)

            for path, expected_content in expected_contents.items():
                if path.exists():
                    content = path.read_text()
                else:
                    content = None
                self.assertEqual(content, expected_content)

    def test_add_missing_part_adds_it(self):
        with self.checking_add_challenge(2020, 1, 'a', True) \
                as (_, combined_info, expected_contents):
            part_info = combined_info.get_part(2020, 1, 'a')
            expected_contents[part_info.path] = \
                DummyBoilerplate.example_part_path.read_text()
            expected_contents[part_info.get_input_filename()] = \
                DummyBoilerplate.example_input_path.read_text()

    def test_add_existing_part_doesnt_overwrite_it(self):
        with self.checking_add_challenge(2020, 1, 'a', False) \
                as (controller, combined_info, expected_contents):
            controller.add_challenge(2020, 1, 'a')
            part_a_py_content = DummyBoilerplate.example_part_path.read_text()\
                .replace("FUNCTION-BODY", 'return "Custom body"')
            day_input_content = "Some input\nFor 2020 1 A"

            part_info = combined_info.get_part(2020, 1, 'a')

            part_info.path.write_text(part_a_py_content)
            part_info.get_input_filename().write_text(day_input_content)

            expected_contents[part_info.path] = part_a_py_content
            expected_contents[part_info.get_input_filename()] = \
                day_input_content
