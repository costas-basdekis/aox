"""
A class that provides an interface, and some boilerplate, for every challenge.
"""

import doctest
import importlib
import sys

from aox.settings import settings_proxy
from aox.utils import has_method_arguments


__all__ = ['PlayNotImplementedError', 'BaseChallenge']


class PlayNotImplementedError(NotImplementedError):
    pass


class BaseChallenge:
    """
    The base class for every challenge.

    The only method that really matters is `solve`, but it also allows for
    specifying a `play` method, that is normally used for interactive
    challenges, or debugging reasons.
    """
    part_a_for_testing = None
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    def __init__(self):
        self.module = self.get_module()
        self.year, self.day, self.part = settings_proxy()\
            .challenges_boilerplate\
            .extract_from_filename(self.module.__file__)
        self.input = self.get_input()

    @classmethod
    def get_module(cls):
        return sys.modules[cls.__module__]

    @classmethod
    def is_main_module(cls):
        main_module = sys.modules.get('__main__')
        return cls.get_module() == main_module

    def get_input(self):
        """Get the input for the challenge"""
        return settings_proxy().challenges_boilerplate\
            .get_day_input_filename(self.year, self.day)\
            .read_text()

    @classmethod
    def main(cls, extra_args=None):
        """
        A way to run the functionality from the command line, but limited to
        only this specific challenge.
        """
        if not cls.is_main_module():
            return
        from aox.command_line.command import cli
        return cli(args=(cls.get_main_args(extra_args=extra_args)))

    @classmethod
    def get_main_args(cls, extra_args=None):
        """The CLI arguments to simulate an invocation of this challenge"""
        if extra_args is None:
            extra_args = sys.argv[1:]
        return [
            'challenge',
            '--path', cls.get_module().__file__,
            '0',
            '0',
            'a',
        ] + extra_args

    # noinspection PyUnusedLocal
    def default_solve(self, _input=None, debugger=None):
        """Convenient method to call `solve` with the input from the disk"""
        if _input is None:
            _input = self.input
        if debugger is None:
            from aox.challenge import Debugger
            debugger = Debugger(enabled=False)
        if has_method_arguments(self.solve, "debugger"):
            return self.solve(_input, debugger=debugger)
        else:
            # noinspection PyArgumentList
            return self.solve(_input, debug=debugger)

    def solve(self, _input, debugger):
        """
        The main method that needs to be overridden by every challenge.

        The solution must be return from this method, either as a number, or as
        a plain string.
        """
        raise NotImplementedError()

    def play(self):
        """
        Some challenges can benefit from providing an interactive or visual
        mode.
        """
        raise PlayNotImplementedError(f"Challenge has not implemented play")

    def get_test_modules(self):
        """
        Get the modules to test. Usually it's the current challenge, but
        sometimes part A also needs to be tested when testing part B, and also
        any other utility functionality not inside either part.
        """
        modules = [
            importlib.import_module(type(self).__module__),
        ]
        if self.part_a_for_testing:
            modules.append(self.part_a_for_testing)
        return modules
