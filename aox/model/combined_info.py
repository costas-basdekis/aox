"""
Combine local and site information about a user's submissions.

The main entry point is `CombinedInfo.from_repo_and_account_infos`.
"""

import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import click

from aox.challenge import BaseChallenge
from aox.model.repo_info import RepoInfo
from aox.model.account_info import AccountInfo
from aox.settings import settings_proxy
from aox.styling.shortcuts import e_error
from aox.utils import try_import_module


__all__ = [
    'CombinedInfo',
    'CombinedYearInfo',
    'CombinedDayInfo',
    'CombinedPartInfo',
]

from aox.web import WebAoc


@dataclass
class CombinedInfo:
    """
    The top level class for combined information: it contains references for all
    the years where challenge part code exists.

    The main entry point is `from_repo_and_account_infos`.
    """
    username: Optional[str]
    total_stars: int
    years_with_code: int
    has_site_data: bool
    year_infos: Dict[int, 'CombinedYearInfo'] = field(default_factory=dict)

    @classmethod
    def from_repo_and_account_infos(
            cls, repo_info: RepoInfo, account_info: Optional[AccountInfo]):
        """Main entry point: combine local and remote information"""
        years_with_code = sum(
            1
            for year_info in repo_info.year_infos.values()
            if year_info.has_code
        )
        if account_info is None:
            combined_info = cls(
                username=None,
                total_stars=0,
                years_with_code=years_with_code,
                has_site_data=False,
            )
        else:
            combined_info = cls(
                username=account_info.username,
                total_stars=account_info.total_stars,
                years_with_code=years_with_code,
                has_site_data=True,
            )
            combined_info.amend_years_from_account_info(account_info)
        combined_info.amend_years_from_repo_info(repo_info)

        return combined_info

    def amend_years_from_account_info(self, account_info):
        """
        Called after creating the instance, to populate the years with remote
        information
        """
        for account_year_info in account_info.year_infos.values():
            if account_year_info.year in self.year_infos:
                year_info = self.year_infos[account_year_info.year]
                year_info.stars = account_year_info.stars
            else:
                # noinspection PyTypeChecker
                year_info = CombinedYearInfo(
                    combined_info=self,
                    year=account_year_info.year,
                    stars=account_year_info.stars,
                    path=None,
                    days_with_code=0,
                )
                self.year_infos[account_year_info.year] = year_info
            year_info.amend_days_from_account_year_info(account_year_info)

    def amend_years_from_repo_info(self, repo_info):
        """
        Called after creating the instance, to populate the years with local
        information
        """
        for repo_year_info in repo_info.year_infos.values():
            days_with_code = sum(
                1
                for day_info in repo_year_info.day_infos.values()
                if day_info.has_code
            )
            if repo_year_info.year in self.year_infos:
                year_info = self.year_infos[repo_year_info.year]
                year_info.path = repo_year_info.path
                year_info.days_with_code = days_with_code
            else:
                year_info = CombinedYearInfo(
                    combined_info=self,
                    year=repo_year_info.year,
                    stars=0,
                    path=repo_year_info.path,
                    days_with_code=days_with_code,
                )
                self.year_infos[repo_year_info.year] = year_info
            year_info.amend_days_from_repo_year_info(repo_year_info)

    @property
    def has_code(self):
        return bool(self.years_with_code)

    def get_challenge_instance(self, year, day, part):
        part_info = self.get_part(year, day, part)
        if not part_info:
            return None
        return part_info.get_challenge_instance()

    def get_year(self, year) \
            -> Optional['CombinedYearInfo']:
        year_info = self.year_infos.get(year)
        if not year_info:
            click.echo(
                f"It looks like there is no code for {e_error(str(year))}")
            return None
        return year_info

    def get_day(self, year, day) \
            -> Optional['CombinedDayInfo']:
        year_info = self.get_year(year)
        if not year_info:
            return None
        return year_info.get_day(day)

    def get_part(self, year, day, part) \
            -> Optional['CombinedPartInfo']:
        day_info = self.get_day(year, day)
        if not day_info:
            return None
        return day_info.get_part(part)

    def serialise(self):
        return {
            "version": 1,
            "username": self.username,
            "total_stars": self.total_stars,
            "years_with_code": self.years_with_code,
            "has_site_data": self.has_site_data,
            "years": {
                str(year): year_info.serialise()
                for year, year_info in self.year_infos.items()
            }
        }


@dataclass
class CombinedYearInfo(object):
    """
    Year information, it contains references for all the days where challenge
    part code or stars exist.
    """
    combined_info: CombinedInfo
    year: int
    stars: int
    path: Path
    days_with_code: int
    day_infos: Dict[int, 'CombinedDayInfo'] = field(default_factory=dict)
    counts_by_part_status: Dict[str, int] = field(
        default_factory=lambda:
        CombinedYearInfo.get_initial_counts_by_part_status())

    @classmethod
    def get_initial_counts_by_part_status(cls):
        """Filler for grouping parts by status"""
        return {
            status: 0
            for status in CombinedPartInfo.STATUSES
        }

    @property
    def relative_path(self):
        return self.path.relative_to(settings_proxy().challenges_root)

    def amend_days_from_account_year_info(self, account_year_info):
        """
        Called after creating the instance, to populate the days with remote
        information
        """
        for account_day_info in account_year_info.day_infos.values():
            if account_day_info.day in self.day_infos:
                day_info = self.day_infos[account_day_info.day]
                day_info.stars = account_day_info.stars
            else:
                # noinspection PyTypeChecker
                day_info = CombinedDayInfo(
                    year_info=self,
                    day=account_day_info.day,
                    stars=account_day_info.stars,
                    path=None,
                    parts_with_code=0,
                )
                self.day_infos[account_day_info.day] = day_info
            day_info.amend_parts_from_account_day_info(account_day_info)
        self.update_counts_by_part_status()

    def amend_days_from_repo_year_info(self, repo_year_info):
        """
        Called after creating the instance, to populate the days with local
        information
        """
        for repo_day_info in repo_year_info.day_infos.values():
            parts_with_code = sum(
                1
                for part_info in repo_day_info.part_infos.values()
                if part_info.has_code
            )
            if repo_day_info.day in self.day_infos:
                day_info = self.day_infos[repo_day_info.day]
                day_info.path = repo_day_info.path
                day_info.parts_with_code = parts_with_code
            else:
                day_info = CombinedDayInfo(
                    year_info=self,
                    day=repo_day_info.day,
                    stars=0,
                    path=repo_day_info.path,
                    parts_with_code=parts_with_code,
                )
                self.day_infos[repo_day_info.day] = day_info
            day_info.amend_parts_from_repo_day_info(repo_day_info)
        self.update_counts_by_part_status()

    def update_counts_by_part_status(self):
        """Group parts by status"""
        for day_info in self.day_infos.values():
            for part_info in day_info.part_infos.values():
                part_info.update_status()
        self.counts_by_part_status.update({
            **self.get_initial_counts_by_part_status(),
            **{
                part_status: len(list(items))
                for part_status, items in itertools.groupby(sorted(
                    part_info.status
                    for day_info in self.day_infos.values()
                    for part_info in day_info.part_infos.values()
                ))
            },
        })

    @property
    def has_code(self):
        return bool(self.days_with_code)

    @property
    def has_site_data(self):
        return self.combined_info.has_site_data

    def get_year_url(self) -> str:
        return WebAoc().get_year_url(self.year)

    def get_day(self, day) -> Optional['CombinedDayInfo']:
        day_info = self.day_infos.get(day)
        if not day_info:
            click.echo(
                f"It looks like there is no code for "
                f"{e_error(f'{self.year} day {day}')}")
            return None
        return day_info

    def get_part(self, day, part) -> Optional['CombinedPartInfo']:
        day_info = self.get_day(day)
        if not day_info:
            return None
        return day_info.get_part(part)

    def serialise(self):
        return {
            "year": self.year,
            "stars": self.stars,
            "days_with_code": self.days_with_code,
            "counts_by_part_status": self.counts_by_part_status,
            "days": {
                str(day): day_info.serialise()
                for day, day_info in self.day_infos.items()
            }
        }


@dataclass
class CombinedDayInfo:
    """
    Day information, it contains references for all the parts where challenge
    part code or stars exist.
    """
    year_info: CombinedYearInfo
    day: int
    stars: int
    path: Path
    parts_with_code: int
    part_infos: Dict[str, 'CombinedPartInfo'] = field(default_factory=dict)

    def amend_parts_from_account_day_info(self, account_day_info):
        """
        Called after creating the instance, to populate the parts with remote
        information
        """
        for account_part_info in account_day_info.part_infos.values():
            if account_part_info.part in self.part_infos:
                part_info = self.part_infos[account_part_info.part]
                part_info.has_star = account_part_info.has_star
                part_info.update_status()
            else:
                # noinspection PyTypeChecker
                part_info = CombinedPartInfo(
                    day_info=self,
                    part=account_part_info.part,
                    has_star=account_part_info.has_star,
                    has_code=False,
                    path=None,
                    status=CombinedPartInfo.STATUS_UNKNOWN,
                    module_name='',
                )
                self.part_infos[account_part_info.part] = part_info

    def amend_parts_from_repo_day_info(self, repo_day_info):
        """
        Called after creating the instance, to populate the parts with local
        information
        """
        for repo_part_info in repo_day_info.part_infos.values():
            if repo_part_info.part in self.part_infos:
                part_info = self.part_infos[repo_part_info.part]
                part_info.path = repo_part_info.path
                part_info.has_code = repo_part_info.has_code
                part_info.module_name = repo_part_info.module_name
            else:
                part_info = CombinedPartInfo(
                    day_info=self,
                    part=repo_part_info.part,
                    has_star=False,
                    path=repo_part_info.path,
                    has_code=repo_part_info.has_code,
                    status=CombinedPartInfo.STATUS_UNKNOWN,
                    module_name=repo_part_info.module_name,
                )
                self.part_infos[repo_part_info.part] = part_info
            part_info.update_status()

    @property
    def year(self):
        return self.year_info.year

    @property
    def relative_path(self):
        return self.path.relative_to(settings_proxy().challenges_root)

    @property
    def has_code(self):
        return bool(self.parts_with_code)

    @property
    def has_site_data(self):
        return self.year_info.has_site_data

    def get_input_filename(self):
        return settings_proxy().challenges_boilerplate\
            .get_day_input_filename(self.year, self.day)

    def get_year_url(self) -> str:
        return self.year_info.get_year_url()

    def get_day_url(self) -> str:
        return WebAoc().get_day_url(self.year, self.day)

    def get_part(self, part) -> Optional['CombinedPartInfo']:
        part_info = self.part_infos.get(part)
        if not part_info:
            click.echo(
                f"It looks like there is no code for "
                f"{e_error(f'{self.year} day {self.day} part {part}')}")
            return None
        return part_info

    def serialise(self):
        return {
            "year": self.year,
            "day": self.day,
            "stars": self.stars,
            "parts_with_code": self.parts_with_code,
            "parts": {
                part: part_info.serialise()
                for part, part_info in self.part_infos.items()
            }
        }


@dataclass
class CombinedPartInfo:
    """
    Part information.
    """
    day_info: CombinedDayInfo
    part: str
    has_star: bool
    has_code: bool
    status: str
    path: Path
    module_name: str

    STATUS_UNKNOWN = 'unknown'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'
    STATUS_DID_NOT_ATTEMPT = 'did-not-attempt'
    STATUS_COULD_NOT_ATTEMPT = 'could-not-attempt'

    STATUSES = [
        STATUS_COMPLETE,
        STATUS_FAILED,
        STATUS_DID_NOT_ATTEMPT,
        STATUS_COULD_NOT_ATTEMPT,
    ]

    def __post_init__(self):
        self.update_status()

    def update_status(self):
        """Update the status, used when we add new information"""
        self.status = self.get_status()

    @property
    def year(self):
        return self.day_info.year

    @property
    def day(self):
        return self.day_info.day

    @property
    def is_final_part(self):
        return (self.day, self.part) == (25, "b")

    @property
    def relative_path(self):
        return self.path.relative_to(settings_proxy().challenges_root)

    @property
    def has_site_data(self):
        return self.day_info.has_site_data

    def get_status(self):
        """Calculate the status, based on the whether it's part A or B"""
        if self.part == 'a':
            return self.get_part_a_status()
        elif self.part == 'b':
            return self.get_part_b_status()
        else:
            raise Exception(f"Unknown part '{self.part}'")

    def get_part_a_status(self):
        """Calculate the status, as if it was part A"""
        if not self.has_site_data:
            return self.STATUS_DID_NOT_ATTEMPT
        elif self.day_info.stars >= 1:
            return self.STATUS_COMPLETE
        elif self.has_code:
            return self.STATUS_FAILED
        else:
            return self.STATUS_DID_NOT_ATTEMPT

    def get_part_b_status(self):
        """Calculate the status, as if it was part B"""
        if not self.has_site_data:
            return self.STATUS_DID_NOT_ATTEMPT
        elif self.day_info.stars == 2:
            return self.STATUS_COMPLETE
        elif self.day_info.stars == 1:
            if self.day == 25 and self.day_info.year_info.stars < 49:
                return self.STATUS_COULD_NOT_ATTEMPT
            elif self.has_code:
                return self.STATUS_FAILED
            else:
                return self.STATUS_DID_NOT_ATTEMPT
        elif self.day_info.part_infos['a'].has_code:
            return self.STATUS_COULD_NOT_ATTEMPT
        else:
            return self.STATUS_DID_NOT_ATTEMPT

    def get_input_filename(self):
        return self.day_info.get_input_filename()

    def get_year_url(self) -> str:
        return self.day_info.get_year_url()

    def get_day_url(self) -> str:
        return self.day_info.get_day_url()

    def get_challenge_instance(self):
        """Get the challenge instance from the module"""
        module = self.get_module()
        if not module:
            return None

        if not hasattr(module, 'challenge'):
            challenge_class = getattr(module, 'Challenge')
            if not isinstance(challenge_class, type) \
                    or not issubclass(challenge_class, BaseChallenge):
                click.echo(
                    f"Challenge {e_error(module.__name__)} does not use "
                    f"`BaseChallenge` and doesn't specify a `challenge` "
                    f"instance")
                return None
            challenge_instance = challenge_class()
        else:
            challenge_instance = getattr(module, 'challenge')

        if not isinstance(challenge_instance, BaseChallenge):
            click.echo(
                f"Challenge {e_error(module.__name__)} `challenge` instance is "
                f"not of `BaseChallenge`")
            return None

        return challenge_instance

    def get_module(self):
        """Load the module for this challenge part"""
        module = try_import_module(self.module_name)
        if not module:
            click.echo(f"Could not find {e_error(self.module_name)}")

        return module

    def serialise(self):
        return {
            "year": self.year,
            "day": self.day,
            "part": self.part,
            "has_star": self.has_star,
            "has_code": self.has_code,
            "status": self.status,
            "module_name": self.module_name,
        }
