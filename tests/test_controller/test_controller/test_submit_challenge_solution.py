from unittest import TestCase
from unittest.mock import patch

import bs4

from aox.utils import get_current_directory
from aox.web import WebAoc
from tests.test_controller.test_controller.test_boilerplate import \
    TestBoilerplate
from tests.utils import using_controller, amending_settings

current_directory = get_current_directory()
submission_replies = current_directory.joinpath('submission_replies')


# noinspection DuplicatedCode
class TestControllerSubmitChallengeSolution(TestCase):
    def check_submit_solution(self, year, day, part, solution, response_path,
                              expected_result):
        if response_path:
            response = bs4.BeautifulSoup(
                response_path.read_text(), 'html.parser')
        else:
            response = None
        with using_controller([], None, interactive=False) \
                as (controller, combined_info, _), \
                amending_settings(challenges_boilerplate=TestBoilerplate()), \
                patch.object(WebAoc, 'submit_solution', return_value=response):
            self.assertEqual(controller.submit_challenge_solution(
                year, day, part, no_prompt=True, solution=solution),
                expected_result)

    def test_submitting_solution_for_non_existing_part_doesnt_attempt(self):
        self.check_submit_solution(2014, 1, 'a', 1, None, (False, False, False))

    def test_no_response_doesnt_submit(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            None,
            (True, False, False))

    def test_right_answer_succeeds(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('right_answer.html'),
            (True, True, True))

    def test_already_completed_succeeds(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('already_completed.html'),
            (True, True, True))

    def test_wrong_answer_fails(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('wrong_answer.html'),
            (True, True, False))

    def test_too_soon_fails(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('too_soon.html'),
            (True, True, False))

    def test_right_final_answer_succeeds(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('right_final_answer.html'),
            (True, True, False))

    def test_unknown_fails(self):
        self.check_submit_solution(
            2020, 1, 'a', "1",
            submission_replies.joinpath('unknown.html'),
            (True, True, False))
