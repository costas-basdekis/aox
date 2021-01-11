"""
The default way to structure parts: `year_xxxx/day_xx/part_x.py`
"""

import re
import shutil
from pathlib import Path

import click

from aox.boilerplate.base_boilerplate import BaseBoilerplate
from aox.settings import settings

from aox.styling.shortcuts import e_warn, e_value
from aox.utils import get_current_directory

current_directory = get_current_directory()


__all__ = ['DefaultBoilerplate']


class DefaultBoilerplate(BaseBoilerplate):
    """The default way to structure parts `year_xxxx/day_xx/part_x.py`"""
    re_filename = re.compile(r"^(?:.*/)?year_(\d+)/day_(\d+)/part_([ab]).py$")

    example_year_path = current_directory\
        .joinpath('default_boilerplate_example_year')
    example_day_path = example_year_path.joinpath('example_day')
    example_part_path = example_day_path.joinpath('example_part.py')

    def extract_from_filename(self, filename):
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
        if not settings.challenges_root:
            return None
        return self.get_day_directory(year, day, relative=relative)\
            .joinpath(f"part_{part}.py")

    def get_day_directory(self, year: int, day: int, relative: bool = False):
        if not settings.challenges_root:
            return None
        return self.get_year_directory(year, relative=relative)\
            .joinpath(f"day_{day:0>2}")

    def get_day_input_filename(self, year: int, day: int,
                               relative: bool = False):
        return self.get_day_directory(year, day, relative=relative)\
            .joinpath("part_a_input.txt")

    def get_year_directory(self, year: int, relative: bool = False):
        if not settings.challenges_root:
            return None
        if relative:
            base = Path()
        else:
            base = settings.challenges_root
        return base.joinpath(f"year_{year}")

    def get_part_module_name(self, year, day, part):
        return ".".join(filter(None, [
            settings.challenges_module_name_root,
            f"year_{year}.day_{day:0>2}.part_{part}",
        ]))

    def create_part(self, year, day, part):
        """Add challenge code boilerplate, if it's not already there"""
        year_path = self.get_year_directory(year)
        day_path = self.get_day_directory(year, day)
        part_path = self.get_part_filename(year, day, part)

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
        if not part_path.exists():
            shutil.copy(self.example_part_path, part_path)

        return True
