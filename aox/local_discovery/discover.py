"""
Gather information about the existence of local code for challenges.

The main entry point is `RepoInfo.from_roots`
"""

import datetime
import glob
import importlib
import itertools
import re


__all__ = ['RepoInfo', 'YearInfo', 'DayInfo', 'PartInfo']

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Dict, Optional


@dataclass
class RepoInfo:
    """
    The top level class for repo information: it contains references for all the
    years where challenge part code exists.

    The main entry point is `from_roots`.
    """
    challenges_root: Optional[Path]
    challenges_module_name_root: Optional[str]
    has_code: bool
    year_infos: Dict[int, 'YearInfo'] = field(default_factory=dict)

    YEARS = list(range(2015, datetime.datetime.now().year + 1))

    @classmethod
    def from_roots(cls, challenges_root, challenges_module_name_root):
        """Create a tree structure, by looking for the expected filenames"""
        if not challenges_root:
            part_filenames = []
        else:
            part_filenames = glob.glob(
                str(challenges_root.joinpath("year_*", "day_*", "part_*.py")))
            root_length = len(f"{challenges_root}/")
            part_filenames = [
                filename[root_length:]
                for filename in part_filenames
            ]

        repo_info = cls(
            challenges_root, challenges_module_name_root, bool(part_filenames))
        repo_info.fill_from_part_filenames(part_filenames)

        return repo_info

    def fill_from_part_filenames(self, filenames):
        """
        Add `YearInfo` instances (and fill them) for each year present in the
        filenames.
        """
        by_year = {
            year: list(year_filenames)
            for year, year_filenames in itertools.groupby(
                sorted(filenames), key=self.get_year_from_filename)
            if year in self.YEARS
        }

        for year, year_filenames in sorted(by_year.items()):
            year_info = YearInfo(
                self, year, bool(year_filenames),
                self.challenges_root.joinpath(f"year_{year}"))
            year_info.fill_from_part_filenames(year_filenames)
            self.year_infos[year] = year_info

    re_filename_year = re.compile(r"^year_(\d+)/.*$")

    def get_year_from_filename(self, filename):
        """Extract the year from the filename"""
        match = self.re_filename_year.match(filename)
        if not match:
            raise Exception(f"Could not get year from filename {filename}")
        year_str, = match.groups()

        return int(year_str)


@dataclass
class YearInfo:
    """
    Year information, it also contains information for all the days where
    challenge part code exists.
    """
    repo_info: 'RepoInfo'
    year: int
    has_code: bool
    path: Path
    day_infos: Dict[int, 'DayInfo'] = field(default_factory=dict)

    DAYS = list(range(1, 26))

    def fill_from_part_filenames(self, filenames):
        """
        Add `DayInfo` instances (and fill them) for each day present in the
        filenames.
        """
        by_day = {
            day: list(day_filenames)
            for day, day_filenames in itertools.groupby(
                sorted(filenames), key=self.get_day_from_filename)
            if day in self.DAYS
        }

        for day, day_filenames in sorted(by_day.items()):
            day_info = DayInfo(
                self, day, bool(day_filenames),
                self.path.joinpath(f"day_{day}"))
            day_info.fill_from_part_filenames(day_filenames)
            self.day_infos[day] = day_info

    re_filename_day = re.compile(r"^year_\d+/day_(\d+)/.*$")

    def get_day_from_filename(self, filename):
        """Extract the day from the filename"""
        day_str, = self.re_filename_day.match(filename).groups()

        return int(day_str)


@dataclass
class DayInfo:
    """
    Day information, it also contains information for all the parts where
    challenge part code exists.
    """
    year_info: YearInfo
    day: int
    has_code: bool
    path: Path
    part_infos: Dict[str, 'PartInfo'] = field(default_factory=dict)

    PARTS = ['a', 'b']

    @property
    def year(self):
        return self.year_info.year

    def fill_from_part_filenames(self, filenames):
        """
        Add `PartInfo` instances (and fill them) for each part present in the
        filenames.
        """
        by_part = {
            part: list(part_filenames)
            for part, part_filenames in itertools.groupby(
                sorted(filenames), key=self.get_part_from_filename)
            if part in self.PARTS
        }

        for part, part_filenames in sorted(by_part.items()):
            part_filename, = part_filenames
            part_info = PartInfo.from_filename(part_filename, self)
            self.part_infos[part] = part_info

    re_filename_part = re.compile(r"^year_\d+/day_\d+/part_([ab]).*$")

    def get_part_from_filename(self, filename):
        """Extract the part from the filename"""
        match = self.re_filename_part.match(filename)
        if not match:
            raise Exception(f"Could not get part from filename {filename}")
        part, = match.groups()

        return part


@dataclass
class PartInfo:
    """Part information."""
    day_info: DayInfo
    part: Literal['a', 'b']
    has_code: bool
    path: Path
    module_name: str

    re_filename_part = re.compile(r"^year_\d+/day_\d+/part_([ab]).*$")

    @property
    def year(self):
        return self.day_info.year

    @property
    def day(self):
        return self.day_info.day

    @classmethod
    def from_filename(cls, filename: str, day_info: DayInfo):
        """Create a `PartInfo` for the filename given"""
        part = cls.get_part_from_filename(filename)
        path = day_info.path.joinpath(f"part_{part}.py")
        module_name = ".".join(filter(None, [
            day_info.year_info.repo_info.challenges_module_name_root,
            f"year_{day_info.year}.day_{day_info.day:0>2}.part_{part}",
        ]))

        return cls(day_info, part, path.exists(), path, module_name)

    @classmethod
    def get_part_from_filename(cls, filename):
        """Extract the part from the filename"""
        match = cls.re_filename_part.match(filename)
        if not match:
            raise Exception(f"Could not get part from filename {filename}")
        part, = match.groups()

        return part

    def get_module(self):
        """Load the module for this challenge part"""
        return importlib.import_module(self.module_name)
