from unittest import TestCase

from tests.test_controller.test_controller.test_boilerplate import \
    DummyBoilerplate
from tests.utils import using_controller, amending_settings


# noinspection DuplicatedCode
class TestControllerRunChallenge(TestCase):
    def check_run_challenge(
            self, year, day, part, force, debug, original_replacement,
            expected_result):
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
            self.assertEqual(controller.run_challenge(
                year, day, part, force, debug), expected_result)

    def test_missing_challenge_doesnt_run(self):
        self.check_run_challenge(2020, 1, 'a', False, [], None, (False, None))

    def test_missing_challenge_is_created_and_runs(self):
        self.check_run_challenge(2020, 1, 'a', True, [], None, (True, None))

    def test_running_challenge_returns_value(self):
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
        self.check_run_challenge(
            2020, 1, 'a', False, [], original_replacement, (True, 42))

    def test_running_challenge_returns_value_with_debug(self):
        original_replacement = (
            "        if debug:\n"
            "            return 4020\n"
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
        self.check_run_challenge(
            2020, 1, 'a', True, [], original_replacement, (True, 4020))
