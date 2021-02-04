"""
The default way to structure parts: `year_xxxx/day_xx/part_x.py`
"""

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import click

from aox.boilerplate.base_boilerplate import BaseBoilerplate
from aox.settings import settings_proxy

from aox.styling.shortcuts import e_warn, e_value, e_error
from aox.utils import get_current_directory

current_directory = get_current_directory()


__all__ = ['DefaultBoilerplate']


@dataclass
class DefaultBoilerplate(BaseBoilerplate):
    """The default way to structure parts `year_xxxx/day_xx/part_x.py`"""
    re_filename = re.compile(r"^(?:.*/)?year_(\d+)/day_(\d+)/part_([ab]).py$")

    example_year_path: Path = current_directory\
        .joinpath('default_boilerplate_example_year')
    example_day_path: Path = example_year_path.joinpath('example_day')
    example_part_path: Path = example_day_path.joinpath('example_part.py')

    def extract_from_filename(self, filename):
        """
        >>> DefaultBoilerplate().extract_from_filename(
        ...     '/home/user/git/my-aoc/year_2020/day_05/part_a.py')
        (2020, 5, 'a')
        >>> DefaultBoilerplate().extract_from_filename(
        ...     'year_2020/day_05/part_a.py')
        (2020, 5, 'a')
        >>> DefaultBoilerplate().extract_from_filename(
        ...     'year_2020/day_15/part_b.py')
        (2020, 15, 'b')
        >>> DefaultBoilerplate().extract_from_filename(
        ...     'year_2020/day_15/part_c.py')
        Traceback (most recent call last):
        ...
        Exception: ...
        >>> DefaultBoilerplate().extract_from_filename(
        ...     'years_2020/day_15/part_a.py')
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        match = self.re_filename.match(filename)
        if not match:
            raise Exception(
                f"Cannot parse filename '{filename}' as a valid challenge part "
                f"filename")

        year_str, day_str, part = match.groups()
        year = int(year_str)
        day = int(day_str)

        return year, day, part

    def get_part_filename(self, year: int, day: int, part: str,
                          relative: bool = False):
        """
        >>> str(DefaultBoilerplate().get_part_filename(2020, 5, 'a', True))
        'year_2020/day_05/part_a.py'
        >>> str(DefaultBoilerplate().get_part_filename(2020, 15, 'a', True))
        'year_2020/day_15/part_a.py'
        """
        day_directory = self.get_day_directory(year, day, relative=relative)
        if day_directory is None:
            return None
        return day_directory.joinpath(f"part_{part}.py")

    def get_day_input_filename(self, year: int, day: int,
                               relative: bool = False):
        """
        >>> str(DefaultBoilerplate().get_day_input_filename(2020, 5, True))
        'year_2020/day_05/input.txt'
        >>> str(DefaultBoilerplate().get_day_input_filename(2020, 15, True))
        'year_2020/day_15/input.txt'
        """
        day_directory = self.get_day_directory(year, day, relative=relative)
        if day_directory is None:
            return None
        return day_directory.joinpath("input.txt")

    def get_day_directory(self, year: int, day: int, relative: bool = False):
        """
        >>> str(DefaultBoilerplate().get_day_directory(2020, 5, True))
        'year_2020/day_05'
        >>> str(DefaultBoilerplate().get_day_directory(2020, 15, True))
        'year_2020/day_15'
        """
        year_directory = self.get_year_directory(year, relative=relative)
        if year_directory is None:
            return None
        return year_directory.joinpath(f"day_{day:0>2}")

    def get_year_directory(self, year: int, relative: bool = False):
        """
        >>> str(DefaultBoilerplate().get_year_directory(2020, True))
        'year_2020'
        """
        if relative:
            base = Path()
        else:
            base = settings_proxy().challenges_root
        if base is None:
            return None
        return base.joinpath(f"year_{year}")

    def get_part_module_name(self, year, day, part):
        """
        >>> DefaultBoilerplate().get_part_module_name(2020, 5, 'a')
        'year_2020.day_05.part_a'
        >>> DefaultBoilerplate().get_part_module_name(2020, 15, 'a')
        'year_2020.day_15.part_a'
        """
        return ".".join(filter(None, [
            settings_proxy().challenges_module_name_root,
            f"year_{year}.day_{day:0>2}.part_{part}",
        ]))

    def create_part(self, year, day, part):
        """Add challenge code boilerplate, if it's not already there"""
        year_path = self.get_year_directory(year)
        day_path = self.get_day_directory(year, day)
        part_path = self.get_part_filename(year, day, part)

        if not any([year_path, day_path, part_path]):
            click.echo(f"You {e_error(f'have not configured')} the root path")
            return False

        if part_path.exists():
            click.echo(
                f"Challenge {e_warn(f'{year} {day} {part.upper()}')} already "
                f"exists at {e_value(str(part_path))}")
            return False

        year_init_path = year_path.joinpath("__init__.py")
        if not year_init_path.exists():
            year_init_path.parent.mkdir(exist_ok=True)
            year_init_path.touch()
        day_init_path = day_path.joinpath("__init__.py")
        if not day_init_path.exists():
            day_init_path.parent.mkdir(exist_ok=True)
            day_init_path.touch()
            part_a_path = self.get_part_filename(year, day, 'a')
            shutil.copy(self.example_part_path, part_a_path)
        day_input_path = day_path.joinpath("input.txt")
        if not day_input_path.exists():
            day_input_path.parent.mkdir(exist_ok=True)
            day_input_path.touch()
        if not part_path.exists():
            shutil.copy(self.example_part_path, part_path)

        return True
