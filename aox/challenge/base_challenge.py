"""
A class that provides an interface, and some boilerplate, for every challenge.
"""

import doctest
import importlib
import re
import sys
from pathlib import Path

from aox.utils import get_current_directory


class BaseChallenge:
    """
    The base class for every challenge.

    The only method that really matters is `solve`, but it also allows for
    specifying a `play` method, that is normally used for interactive
    challenges, or debugging reasons.
    """
    part_a_for_testing = None
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    re_part = re.compile(r"part_([ab])")
    re_day = re.compile(r"day_(\d\d)")
    re_year = re.compile(r"year_(\d\d\d\d)")

    def __init__(self):
        self.module = sys.modules[self.__module__]
        self.input = self.get_input()
        self.part = self.get_part()
        self.day = self.get_day()
        self.year = self.get_year()

    def get_part(self):
        """Parse the part from the filename"""
        path = Path(self.module.__file__)
        part_name = path.name
        part_match = self.re_part.match(part_name)
        if not part_match:
            raise Exception(
                f"Challenge name is not a recognised part 'part_x': "
                f"{part_name}")

        part, = part_match.groups()

        return part

    def get_day(self):
        """Parse the day from the filename"""
        path = Path(self.module.__file__)
        day_name = path.parent.name
        day_match = self.re_day.match(day_name)
        if not day_match:
            raise Exception(
                f"Challenge path is not a recognised day 'day_xx': "
                f"{day_name}")

        day_text, = day_match.groups()
        day = int(day_text)

        return day

    def get_year(self):
        """Parse the year from the filename"""
        path = Path(self.module.__file__)
        year_name = path.parent.parent.name
        year_match = self.re_year.match(year_name)
        if not year_match:
            raise Exception(
                f"Challenge path is not a recognised year 'year_xxxx': "
                f"{year_name}")

        year_text, = year_match.groups()
        year = int(year_text)

        return year

    def get_input(self):
        """Get the input for the challenge"""
        return get_current_directory(self.module.__file__)\
            .joinpath("part_a_input.txt") \
            .read_text()

    def main(self):
        """
        A way to run the functionality from the command line, but limited to
        only this specific challenge.
        """
        main_module = sys.modules.get('__main__')
        if self.module != main_module:
            return
        from aox.command_line.command import cli
        cli(args=(self.get_main_args()))

    def get_main_args(self):
        """The CLI arguments to simulate an invocation of this challenge"""
        return [
            'challenge',
            str(self.year),
            str(self.day),
            self.part,
        ] + sys.argv[1:]

    def default_solve(self, _input=None, debug=False):
        """Convenient method to call `solve` with the input from the disk"""
        if _input is None:
            _input = self.input
        return self.solve(_input, debug=debug)

    def solve(self, _input, debug=False):
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
        raise Exception(f"Challenge has not implemented play")

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
