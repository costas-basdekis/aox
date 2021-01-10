"""
Gather stars from the AOC site.

The main entry point is `AccountInfo.from_site`
"""
import json
import re
from dataclasses import dataclass, field
from typing import Dict

import click

from aox.settings import settings
from aox.styling.shortcuts import e_error
from aox.web import WebAoc

__all__ = [
    'AccountInfo',
    'AccountYearInfo',
    'AccountDayInfo',
    'AccountPartInfo',
]


@dataclass
class AccountInfo:
    """
    The top level class for account information: it contains references for all
    the years where a challenge part star exists.

    The main entry point is `from_site`.
    """
    username: str
    total_stars: int
    year_infos: Dict[int, 'AccountYearInfo'] = field(default_factory=dict)

    @classmethod
    def from_site(cls):
        """Scrape the site for the stars for each challenge"""
        events_page = WebAoc().get_events_page()
        if not events_page:
            return None

        username = cls.get_username(events_page)
        if not username:
            return None

        total_stars = cls.get_total_stars(events_page)

        account_info = cls(username, total_stars)
        account_info.fill_years_from_site(events_page)

        return account_info

    @classmethod
    def get_username(cls, events_page):
        """
        Extract the username. If there isn't a username, there is no information
        to gather.
        """
        user_nodes = events_page.select(".user")
        if not user_nodes:
            click.echo(
                f"Either the session ID in {e_error('AOC_SESSION_ID')} is "
                f"wrong, or it has expired: could not find the user name")
            return None

        user_node = user_nodes[0]
        text_children = [
            child
            for child in user_node.children
            if isinstance(child, str)
        ]
        if not text_children:
            click.echo(
                f"Either the user name is blank or the format has changed")
            return None
        return text_children[0].strip()

    @classmethod
    def get_total_stars(cls, events_page):
        """Grab the total stars"""
        total_stars_nodes = events_page.select("p > .star-count")
        return cls.parse_star_count(total_stars_nodes)

    re_stars = re.compile(r'^(\d+)\*$')

    @classmethod
    def parse_star_count(cls, stars_nodes, default=None):
        """Star counts are represented in the same way everywhere"""
        if not stars_nodes:
            return default
        stars_node = stars_nodes[0]
        stars_match = cls.re_stars.match(stars_node.text.strip())
        if not stars_match:
            return default

        stars_text, = stars_match.groups()
        return int(stars_text)

    @classmethod
    def from_cache(cls):
        if not settings.site_data_path:
            return None

        with settings.site_data_path.open() as f:
            serialised = json.load(f)

        return cls.deserialise(serialised)

    @classmethod
    def deserialise(cls, serialised):
        """Read the data from JSON. The data are versioned"""
        if serialised is None:
            return None

        version = serialised.get("version", 0)
        if version == 0:
            return cls.deserialise_v0(serialised)
        elif version == 1:
            return cls.deserialise_v1(serialised)
        elif version == 2:
            return cls.deserialise_v2(serialised)
        else:
            raise Exception(f"Not aware of account info version '{version}'")

    @classmethod
    def deserialise_v0(cls, serialised):
        """Read the data from for version 0"""
        account_info = cls(
            username=serialised['user_name'],
            total_stars=serialised['total_stars'],
        )
        account_info.fill_years_from_serialised(serialised['years'], version=0)

        return account_info

    @classmethod
    def deserialise_v1(cls, serialised):
        """Read the data from for version 1"""
        account_info = cls(
            username=serialised['username'],
            total_stars=serialised['total_stars'],
        )
        account_info.fill_years_from_serialised(serialised['years'], version=1)

        return account_info

    @classmethod
    def deserialise_v2(cls, serialised):
        """Read the data from for version 2"""
        account_info = cls(
            username=serialised['username'],
            total_stars=serialised['total_stars'],
        )
        account_info.fill_years_from_serialised(serialised['years'], version=2)

        return account_info

    def fill_years_from_site(self, events_page):
        """Parse the years information from the site"""
        stars_nodes = events_page.select(".eventlist-event .star-count")
        years_nodes = [node.parent for node in stars_nodes]
        years_and_stars = [
            (year, stars)
            for year, stars
            in filter(None, map(self.get_year_and_stars, years_nodes))
            if stars
        ]
        for year, stars in years_and_stars:
            year_info = AccountYearInfo(self, year, stars)
            year_info.fill_days_from_site()
            self.year_infos[year] = year_info

    re_year = re.compile(r'^\[(\d+)]$')

    def get_year_and_stars(self, year_node):
        """Get the stars for a year from a year node in the events page"""
        year_name_node = year_node.findChild('a')
        if not year_name_node:
            return None
        year_name_match = self.re_year.match(year_name_node.text)
        if not year_name_match:
            return None
        year_text, = year_name_match.groups()
        year = int(year_text)

        stars_nodes = year_node.select('.star-count')
        stars = self.parse_star_count(stars_nodes, default=0)

        return year, stars

    def fill_years_from_serialised(self, serialised_years, version):
        """Parse the years from JSON. The data are versioned"""
        if version == 0:
            self.fill_years_from_serialised_v0(serialised_years)
        elif version == 1:
            self.fill_years_from_serialised_v1(serialised_years)
        elif version == 2:
            self.fill_years_from_serialised_v2(serialised_years)
        else:
            raise Exception(f"Not aware of account info version '{version}'")

    def fill_years_from_serialised_v0(self, serialised_years):
        """Parse the years from JSON version 0"""
        for year_str, serialised_year in serialised_years.items():
            year = int(year_str)
            year_info = AccountYearInfo.deserialise(
                serialised_year, 0, self)
            self.year_infos[year] = year_info

    def fill_years_from_serialised_v1(self, serialised_years):
        """Parse the years from JSON version 1"""
        for year_str, serialised_year in serialised_years.items():
            year = int(year_str)
            year_info = AccountYearInfo.deserialise(
                {"year": year, **serialised_year}, 1, self)
            self.year_infos[year] = year_info

    def fill_years_from_serialised_v2(self, serialised_years):
        """Parse the years from JSON version 2"""
        for year_str, serialised_year in serialised_years.items():
            year = int(year_str)
            year_info = AccountYearInfo.deserialise(
                {"year": year, **serialised_year}, 2, self)
            self.year_infos[year] = year_info

    def serialise(self):
        """Convert to JSON. The data are versioned"""
        return {
            "version": 2,
            "username": self.username,
            "total_stars": self.total_stars,
            "years": {
                str(year): year_info.serialise()
                for year, year_info in self.year_infos.items()
            }
        }


@dataclass
class AccountYearInfo:
    """
    Year information, it also contains information for all the days where a
    challenge part star exists.
    """
    account_info: AccountInfo
    year: int
    stars: int
    day_infos: Dict[int, 'AccountDayInfo'] = field(default_factory=dict)

    @classmethod
    def deserialise(cls, serialised, version, account_info):
        """Read the data from JSON. The data are versioned"""
        if version == 0:
            return cls.from_serialised_v0(serialised, account_info)
        elif version == 1:
            return cls.from_serialised_v1(serialised, account_info)
        elif version == 2:
            return cls.from_serialised_v2(serialised, account_info)
        else:
            raise Exception(
                f"Not aware of account year info version '{version}'")

    @classmethod
    def from_serialised_v0(cls, serialised, account_info):
        """Read the data from for version 0"""
        year_info = cls(
            account_info=account_info,
            year=serialised["year"],
            stars=serialised["stars"],
        )
        year_info.fill_days_from_serialised(serialised["days"], version=0)

        return year_info

    @classmethod
    def from_serialised_v1(cls, serialised, account_info):
        """Read the data from for version 1"""
        year_info = cls(
            account_info=account_info,
            year=serialised["year"],
            stars=serialised["stars"],
        )
        year_info.fill_days_from_serialised(serialised["days"], version=1)

        return year_info

    @classmethod
    def from_serialised_v2(cls, serialised, account_info):
        """Read the data from for version 2"""
        year_info = cls(
            account_info=account_info,
            year=serialised["year"],
            stars=serialised["stars"],
        )
        year_info.fill_days_from_serialised(serialised["days"], version=2)

        return year_info

    def fill_days_from_site(self):
        """Parse the days information from the site"""
        year_page = WebAoc().get_year_page(self.year)
        if year_page is None:
            return

        days_nodes = year_page.select('.calendar > a[class^="calendar-day"]')
        for day_node in days_nodes:
            day_info = AccountDayInfo.from_day_node(day_node, self)
            if not day_info:
                continue
            self.day_infos[day_info.day] = day_info

    def fill_days_from_serialised(self, serialised_days, version):
        """Parse the years from JSON. The data are versioned"""
        if version == 0:
            self.fill_days_from_serialised_v0(serialised_days)
        elif version == 1:
            self.fill_days_from_serialised_v1(serialised_days)
        elif version == 2:
            self.fill_days_from_serialised_v2(serialised_days)
        else:
            raise Exception(
                f"Not aware of account year info version '{version}'")

    def fill_days_from_serialised_v0(self, serialised_days):
        """Read the data from for version 0"""
        for day_str, day_stars in serialised_days.items():
            day = int(day_str)
            day_info = AccountDayInfo.deserialise(
                {"day": day, "stars": day_stars}, 0, self)
            self.day_infos[day] = day_info

    def fill_days_from_serialised_v1(self, serialised_days):
        """Read the data from for version 1"""
        for day_str, serialised_day in serialised_days.items():
            day = int(day_str)
            day_info = AccountDayInfo.deserialise(serialised_day, 1, self)
            self.day_infos[day] = day_info

    def fill_days_from_serialised_v2(self, serialised_days):
        """Read the data from for version 2"""
        for day_str, serialised_day in serialised_days.items():
            day = int(day_str)
            day_info = AccountDayInfo.deserialise(serialised_day, 2, self)
            self.day_infos[day] = day_info

    def serialise(self):
        """Convert to JSON. The data are versioned"""
        return {
            "year": self.year,
            "stars": self.stars,
            "days": {
                str(day): day_info.serialise()
                for day, day_info in self.day_infos.items()
            }
        }


@dataclass
class AccountDayInfo:
    """
    Year information, it also contains information for all the parts where a
    star exists.
    """
    year_info: AccountYearInfo
    day: int
    stars: int
    part_infos: Dict[str, 'AccountPartInfo'] = field(default_factory=dict)

    @classmethod
    def from_day_node(cls, day_node, year_info):
        """Parse the day info from a node in year page"""
        day_name_nodes = day_node.select(".calendar-day")
        if not day_name_nodes:
            return None
        day_name_node = day_name_nodes[0]
        day_text = day_name_node.text
        try:
            day = int(day_text)
        except ValueError:
            return None

        class_names = day_node.attrs['class']
        if 'calendar-verycomplete' in class_names:
            stars = 2
        elif 'calendar-complete' in class_names:
            stars = 1
        else:
            stars = 0

        day_info = cls(year_info, day, stars)
        day_info.fill_parts()

        return day_info

    @classmethod
    def deserialise(cls, serialised, version, year_info):
        """Read the data from JSON. The data are versioned"""
        if version == 0:
            return cls.from_serialised_v0(serialised, year_info)
        elif version == 1:
            return cls.from_serialised_v1(serialised, year_info)
        elif version == 2:
            return cls.from_serialised_v2(serialised, year_info)
        else:
            raise Exception(
                f"Not aware of account day info version '{version}'")

    @classmethod
    def from_serialised_v0(cls, serialised, year_info):
        """Read the data from for version 0"""
        day_info = cls(
            year_info=year_info,
            day=serialised["day"],
            stars=serialised["stars"],
        )
        day_info.fill_parts()

        return day_info

    @classmethod
    def from_serialised_v1(cls, serialised, year_info):
        """Read the data from for version 1"""
        day_info = cls(
            year_info=year_info,
            day=serialised["day"],
            stars=serialised["stars"],
        )
        day_info.fill_parts_from_serialised(serialised["parts"], version=1)

        return day_info

    @classmethod
    def from_serialised_v2(cls, serialised, year_info):
        """Read the data from for version 2"""
        day_info = cls(
            year_info=year_info,
            day=serialised["day"],
            stars=serialised["stars"],
        )
        day_info.fill_parts_from_serialised(serialised["parts"], version=2)

        return day_info

    @property
    def year(self):
        return self.year_info.year

    def fill_parts(self):
        """Fill part infos just from the stars"""
        for part, min_stars in ('a', 1), ('b', 2):
            self.part_infos[part] = AccountPartInfo(
                self, part, self.stars >= min_stars)

    def fill_parts_from_serialised(self, serialised_parts, version):
        """Parse the years from JSON. The data are versioned"""
        if version == 1:
            self.fill_parts_from_serialised_v1(serialised_parts)
        if version == 2:
            self.fill_parts_from_serialised_v2(serialised_parts)
        else:
            raise Exception(
                f"Not aware of account day info version '{version}'")

    def fill_parts_from_serialised_v1(self, serialised_parts):
        """Parse the years from JSON version 1"""
        for part, serialised_part in serialised_parts.items():
            part_info = AccountPartInfo.deserialise(
                serialised_part, 1, self)
            self.part_infos[part] = part_info

    def fill_parts_from_serialised_v2(self, serialised_parts):
        """Parse the years from JSON version 2"""
        for part, serialised_part in serialised_parts.items():
            part_info = AccountPartInfo.deserialise(
                serialised_part, 2, self)
            self.part_infos[part] = part_info

    def serialise(self):
        """Convert to JSON. The data are versioned"""
        return {
            "year": self.year,
            "day": self.day,
            "stars": self.stars,
            "parts": {
                part: part_info.serialise()
                for part, part_info in self.part_infos.items()
            }
        }


@dataclass
class AccountPartInfo:
    """
    Year information, it also contains information for a part.
    """
    day_info: AccountDayInfo
    part: str
    has_star: bool

    @classmethod
    def deserialise(cls, serialised, version, day_info):
        """Read the data from JSON. The data are versioned"""
        if version == 1:
            return cls.deserialise_v1(serialised, day_info)
        elif version == 2:
            return cls.deserialise_v2(serialised, day_info)
        else:
            raise Exception(
                f"Not aware of account part info version '{version}'")

    @classmethod
    def deserialise_v1(cls, serialised, day_info):
        """Parse the years from JSON version 1"""
        return cls(
            day_info=day_info,
            part=serialised["part"],
            has_star=bool(serialised["stars"]),
        )

    @classmethod
    def deserialise_v2(cls, serialised, day_info):
        """Parse the years from JSON version 1"""
        return cls(
            day_info=day_info,
            part=serialised["part"],
            has_star=serialised["has_star"],
        )

    @property
    def year(self):
        return self.day_info.year

    @property
    def day(self):
        return self.day_info.day

    def serialise(self):
        """Convert to JSON. The data are versioned"""
        return {
            "year": self.year,
            "day": self.day,
            "part": self.part,
            "has_star": self.has_star,
        }
