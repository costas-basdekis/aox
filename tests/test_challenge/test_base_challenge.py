from unittest import TestCase, mock

from tests.utils import making_combined_info


class TestBaseChallenge(TestCase):
    def test_parsed_year_day_and_part(self):
        with making_combined_info([(2020, 3, 'a')], None) as combined_info:
            challenge = combined_info.get_challenge_instance(2020, 3, 'a')
            self.assertIsNotNone(challenge)
            self.assertEqual(
                (challenge.year, challenge.day, challenge.part),
                (2020, 3, 'a'))

    def test_input(self):
        with making_combined_info([(2020, 3, 'a')], None) as combined_info:
            part = combined_info.get_part(2020, 3, 'a')
            part.get_input_filename()\
                .write_text("Custom Input\nOver Multiple\nLines")
            challenge = combined_info.get_challenge_instance(2020, 3, 'a')
            self.assertEqual(
                challenge.input, "Custom Input\nOver Multiple\nLines")

    def test_input_is_given_through_default_solve(self):
        with making_combined_info([(2020, 3, 'a')], None) as combined_info:
            part = combined_info.get_part(2020, 3, 'a')
            part.get_input_filename()\
                .write_text("Custom Input\nOver Multiple\nLines")
            challenge = combined_info.get_challenge_instance(2020, 3, 'a')
            with mock.patch.object(challenge, 'solve') as mocked:
                challenge.default_solve()
                self.assertEqual(mocked.call_count, 1)
                self.assertEqual(
                    mocked.call_args,
                    mock.call(
                        "Custom Input\nOver Multiple\nLines", debug=False))

    def test_main_doesnt_run_if_not_main(self):
        with making_combined_info([(2020, 3, 'a')], None) as combined_info:
            challenge = combined_info.get_challenge_instance(2020, 3, 'a')

            with mock.patch.object(challenge, 'solve') as mocked:
                challenge.main([])
                self.assertEqual(mocked.call_count, 0)

    def test_main_runs_if_main(self):
        with making_combined_info([(2020, 3, 'a')], None) as combined_info:
            part = combined_info.get_part(2020, 3, 'a')
            part.get_input_filename()\
                .write_text("Custom Input\nOver Multiple\nLines")
            challenge = combined_info.get_challenge_instance(2020, 3, 'a')

            with mock.patch.object(challenge, 'solve') as solve_mocked:
                with mock.patch.object(type(challenge), 'is_main_module') \
                        as is_main_module_mocked:
                    is_main_module_mocked.return_value = True
                    with self.assertRaises(SystemExit):
                        challenge.main([])
                    self.assertEqual(solve_mocked.call_count, 1)
                    self.assertEqual(
                        solve_mocked.call_args,
                        mock.call(
                            "Custom Input\nOver Multiple\nLines", debug=False))
