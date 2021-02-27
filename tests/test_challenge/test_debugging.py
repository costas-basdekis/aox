from contextlib import contextmanager
from unittest import TestCase

from aox.challenge import Debugger
from tests.utils import capturing_stdout, amending_settings


class TestDebugging(TestCase):
    @contextmanager
    def assert_output(self, expected):
        with self.getting_output() as captured:
            yield
        self.assertEqual(captured.getvalue(), expected)

    @contextmanager
    def getting_output(self):
        with amending_settings(
                default_debugger_report_format=self.concise_debugger_format):
            with capturing_stdout() as captured:
                yield captured

    def concise_debugger_format(self, debugger, message):
        return f"Message: {message}, extra: extra"

    def wrapping_debugger_format(self, debugger, message):
        return f"[{message}]"

    def wrapping_debugger_format_2(self, debugger, message):
        return f"<{message}>"

    def wrapping_debugger_format_3(self, debugger, message):
        return f"({message})"

    def test_default_report(self):
        with self.assert_output("Message: Hello, extra: extra\n"):
            Debugger().default_report("Hello")

    def test_extra_report(self):
        with self.assert_output("Message: [Hello], extra: extra\n"):
            Debugger(extra_report_formats=[self.wrapping_debugger_format])\
                .default_report("Hello")

    def test_adding_extra_report_format(self):
        with self.assert_output("Message: [Hello], extra: extra\n"):
            debugger = Debugger()
            with debugger.adding_extra_report_format(
                    self.wrapping_debugger_format):
                debugger.default_report("Hello")

    def test_adding_extra_report_format_multiple(self):
        with self.assert_output("Message: [<(Hello)>], extra: extra\n"):
            debugger = Debugger()
            with debugger.adding_extra_report_format(
                    self.wrapping_debugger_format):
                with debugger.adding_extra_report_format(
                        self.wrapping_debugger_format_2):
                    with debugger.adding_extra_report_format(
                            self.wrapping_debugger_format_3):
                        debugger.default_report("Hello")
