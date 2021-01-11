"""
Gather information about the existence of local code for challenges.

The main entry point is `RepoInfo.from_roots`
"""

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Dict, Optional

from aox.settings import settings

__all__ = ['RepoInfo', 'RepoYearInfo', 'RepoDayInfo', 'RepoPartInfo']


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
    year_infos: Dict[int, 'RepoYearInfo'] = field(default_factory=dict)

    YEARS = list(range(2015, datetime.datetime.now().year + 1))

    @classmethod
    def from_roots(cls, challenges_root=None, challenges_module_name_root=None):
        """Create a tree structure, by looking for the expected filenames"""
        if challenges_root is None:
            challenges_root = settings.challenges_root
        if challenges_module_name_root is None:
            challenges_module_name_root = settings.challenges_module_name_root
        repo_info = cls(
            challenges_root=challenges_root,
            challenges_module_name_root=challenges_module_name_root,
            has_code=False,
        )
        repo_info.fill()
        return repo_info

    def fill(self):
        """
        Add `RepoYearInfo` instances (and fill them) for each year present in
        the filenames.
        """
        for year in self.YEARS:
            self.year_infos[year] = RepoYearInfo.from_year(year, self)
        self.has_code = any(
            year_info.has_code
            for year_info in self.year_infos.values()
        )


@dataclass
class RepoYearInfo:
    """
    Year information, it also contains information for all the days where
    challenge part code exists.
    """
    repo_info: 'RepoInfo'
    year: int
    has_code: bool
    path: Path
    day_infos: Dict[int, 'RepoDayInfo'] = field(default_factory=dict)

    DAYS = list(range(1, 26))

    @classmethod
    def from_year(cls, year, repo_info):
        year_info = cls(
            repo_info=repo_info,
            year=year,
            has_code=False,
            path=settings.challenges_boilerplate.get_year_directory(year),
        )
        year_info.fill()
        return year_info

    def fill(self):
        """
        Add `RepoDayInfo` instances (and fill them) for each day present in the
        filenames.
        """
        for day in self.DAYS:
            self.day_infos[day] = RepoDayInfo.from_day(day, self)
        self.has_code = any(
            day_info.has_code
            for day_info in self.day_infos.values()
        )


@dataclass
class RepoDayInfo:
    """
    Day information, it also contains information for all the parts where
    challenge part code exists.
    """
    year_info: RepoYearInfo
    day: int
    has_code: bool
    path: Path
    part_infos: Dict[str, 'RepoPartInfo'] = field(default_factory=dict)

    PARTS = ['a', 'b']

    @classmethod
    def from_day(cls, day, year_info):
        day_info = cls(
            year_info=year_info,
            day=day,
            has_code=False,
            path=settings.challenges_boilerplate.get_day_directory(
                year_info.year, day),
        )
        day_info.fill()
        return day_info

    @property
    def year(self):
        return self.year_info.year

    def fill(self):
        """
        Add `RepoPartInfo` instances (and fill them) for each part present in
        the filenames.
        """
        for part in self.PARTS:
            self.part_infos[part] = RepoPartInfo.from_part(part, self)
        self.has_code = any(
            part_info.has_code
            for part_info in self.part_infos.values()
        )


@dataclass
class RepoPartInfo:
    """Part information."""
    day_info: RepoDayInfo
    part: Literal['a', 'b']
    has_code: bool
    path: Path
    module_name: str

    @property
    def year(self):
        return self.day_info.year

    @property
    def day(self):
        return self.day_info.day

    @classmethod
    def from_part(cls, part, day_info):
        path = settings.challenges_boilerplate.get_part_filename(
            day_info.year, day_info.day, part)
        module_name = settings.challenges_boilerplate.get_part_module_name(
            day_info.year, day_info.day, part)

        return cls(day_info, part, path.exists(), path, module_name)
