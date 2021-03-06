# flake8: noqa E501
import doctest
from unittest import TestCase

from tests.test_controller.test_controller.test_boilerplate import \
    DummyBoilerplate
from tests.utils import using_controller, amending_settings


# noinspection DuplicatedCode
class TestControllerTestAndRunChallenge(TestCase):
    def check_test_and_run_challenge(
            self, year, day, part, force, filter_texts, debug,
            original_replacement, expected_result):
        with using_controller([], None, interactive=False) \
                as (controller, combined_info, _), \
                amending_settings(challenges_boilerplate=DummyBoilerplate()):
            if original_replacement is not None:
                controller.add_challenge(year, day, part)
                part_info = combined_info.get_part(year, day, part)
                code = part_info.path.read_text()
                code = code.replace(
                    '        "FUNCTION-BODY"', original_replacement)
                part_info.path.write_text(code)
            yield controller, combined_info
            self.assertEqual(controller.test_and_run_challenge(
                year, day, part, force, filter_texts, debug), expected_result)

    def test_missing_challenge_doesnt_test_and_run(self):
        self.check_test_and_run_challenge(2020, 1, 'a', False, [], False, None,
                                          (False, None, None))

    def test_missing_challenge_is_created_and_tests_and_runs(self):
        self.check_test_and_run_challenge(
            2020, 1, 'a', True, [], False, None,
            (True, doctest.TestResults(failed=1, attempted=1), None))

    def test_testing_challenge_runs_successful_tests_and_runs(self):
        original_replacement = (
            "        return 42\n"
            "    def foo(self):\n"
            "        '''\n"
            "        >>> Challenge().foo()\n"
            "        'Success'\n"
            "        '''\n"
            "        return 'Success'\n"
            "def another():\n"
            "    '''\n"
            "    >>> another()\n"
            "    [0, 1, 2]\n"
            "    '''\n"
            "    return list(range(3))\n"
        )
        self.check_test_and_run_challenge(
            2020, 1, 'a', False, [], False, original_replacement,
            (True, doctest.TestResults(failed=0, attempted=3), 42))

    def test_testing_challenge_runs_unsuccessful_tests_and_runs(self):
        original_replacement = (
            "        return 42\n"
            "    def foo(self):\n"
            "        '''\n"
            "        >>> Challenge().foo()\n"
            "        'Success'\n"
            "        '''\n"
            "        return 'Failure'\n"
            "def another():\n"
            "    '''\n"
            "    >>> another()\n"
            "    [0, 1, 2]\n"
            "    '''\n"
            "    return list(range(3))\n"
        )
        self.check_test_and_run_challenge(
            2020, 1, 'a', False, [], False, original_replacement,
            (True, doctest.TestResults(failed=1, attempted=3), 42))

    def test_testing_challenge_runs_only_selected_tests_and_runs(self):
        original_replacement = (
            "        return 24\n"
            "    def foo(self):\n"
            "        '''\n"
            "        >>> Challenge().foo()\n"
            "        'Success'\n"
            "        '''\n"
            "        return 'Failure'\n"
            "def another():\n"
            "    '''\n"
            "    >>> another()\n"
            "    [0, 1, 2]\n"
            "    '''\n"
            "    return list(range(3))\n"
        )
        self.check_test_and_run_challenge(
            2020, 1, 'a', False, ['another'], False, original_replacement,
            (True, doctest.TestResults(failed=0, attempted=1), 24))

    def test_testing_challenge_runs_only_selected_tests_and_runs_with_debug(self):
        original_replacement = (
            "        if debug:\n"
            "            return 2040\n"
            "        return 24\n"
            "    def foo(self):\n"
            "        '''\n"
            "        >>> Challenge().foo()\n"
            "        'Success'\n"
            "        '''\n"
            "        return 'Failure'\n"
            "def another():\n"
            "    '''\n"
            "    >>> another()\n"
            "    [0, 1, 2]\n"
            "    '''\n"
            "    return list(range(3))\n"
        )
        self.check_test_and_run_challenge(
            2020, 1, 'a', False, ['another'], True, original_replacement,
            (True, doctest.TestResults(failed=0, attempted=1), 2040))
