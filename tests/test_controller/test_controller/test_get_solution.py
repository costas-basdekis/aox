# flake8: noqa E501
from unittest import TestCase

from tests.test_controller.test_controller.test_boilerplate import \
    TestBoilerplate
from tests.utils import using_controller, amending_settings


# noinspection DuplicatedCode
class TestControllerGetSolution(TestCase):
    def check_get_solution(self, year, day, part, force, solution,
                           original_replacement, expected_result):
        with using_controller([], None, interactive=False) \
                as (controller, combined_info, _), \
                amending_settings(challenges_boilerplate=TestBoilerplate()):
            if original_replacement is not None:
                controller.add_challenge(year, day, part)
                part_info = combined_info.get_part(year, day, part)
                code = part_info.path.read_text()
                code = code.replace(
                    '        "FUNCTION-BODY"', original_replacement)
                part_info.path.write_text(code)
            self.assertEqual(controller.get_solution(
                year, day, part, force=force, no_prompt=True,
                solution=solution),
                expected_result)

    def test_getting_solution_from_non_existing_part_doesnt_get_it(self):
        self.check_get_solution(2014, 1, 'a', False, 1, None, None)

    def test_getting_solution_from_non_existing_part_with_provided_returns_it(self):
        self.check_get_solution(2020, 1, 'a', False, 1, None, "1")

    def test_getting_solution_from_existing_part_with_provided_returns_it(self):
        self.check_get_solution(2020, 1, 'a', False, 1, (
            "        return 2\n"
        ), "1")

    def test_getting_solution_from_existing_part_runs_and_returns(self):
        self.check_get_solution(2020, 1, 'a', False, None, (
            "        return 2\n"
        ), "2")
