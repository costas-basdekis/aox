"""
Gather stars from the AOC site.

The main entry point is `AccountInfo.from_site`
"""

import json
from dataclasses import dataclass, field
from typing import Dict

from aox.settings import settings_proxy
from aox.web import AccountScraper

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
        collected_data = AccountScraper().collect_data()
        return cls.from_collected_data(collected_data)

    @classmethod
    def from_collected_data(cls, collected_data):
        """
        >>> AccountInfo.from_collected_data({
        ...     "username": "Test User", "total_stars": 5, "years": {
        ...         2020: {"year": 2020, "stars": 5, "days": {
        ...             1: 2,
        ...             2: 1,
        ...             3: 0,
        ...         }}}})
        AccountInfo(username='Test User', total_stars=5, year_infos={2020:
            AccountYearInfo(account_info=..., year=2020, stars=5,
                day_infos={1: AccountDayInfo(year_info=..., day=1, stars=2,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=True),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=True)}),
                2: AccountDayInfo(year_info=..., day=2, stars=1,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=True),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=False)}),
                3: AccountDayInfo(year_info=..., day=3, stars=0,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=False),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=False)})})})
        """
        if collected_data is None:
            return None

        username = collected_data['username']
        if not username:
            return None

        total_stars = collected_data['total_stars']

        account_info = cls(username, total_stars)
        account_info.fill_years_from_collected_data(collected_data)

        return account_info

    @classmethod
    def from_cache(cls):
        site_data_path = settings_proxy().site_data_path
        if not site_data_path or not site_data_path.exists():
            return None

        with site_data_path.open() as f:
            serialised = json.load(f)

        return cls.deserialise(serialised)

    @classmethod
    def deserialise(cls, serialised):
        """
        Read the data from JSON. The data are versioned

        >>> AccountInfo.deserialise(AccountInfo.from_collected_data({
        ...     "username": "Test User", "total_stars": 5, "years": {
        ...         2020: {"year": 2020, "stars": 5, "days": {
        ...             1: 2,
        ...             2: 1,
        ...             3: 0,
        ...         }}}}).serialise())
        AccountInfo(username='Test User', total_stars=5, year_infos={2020:
            AccountYearInfo(account_info=..., year=2020, stars=5,
                day_infos={1: AccountDayInfo(year_info=..., day=1, stars=2,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=True),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=True)}),
                2: AccountDayInfo(year_info=..., day=2, stars=1,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=True),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=False)}),
                3: AccountDayInfo(year_info=..., day=3, stars=0,
                    part_infos={'a':
                        AccountPartInfo(day_info=..., part='a', has_star=False),
                        'b': AccountPartInfo(day_info=..., part='b',
                            has_star=False)})})})
        """
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

    def fill_years_from_collected_data(self, collected_data):
        """Parse the years information from collected data"""
        for year_data in collected_data['years'].values():
            year_info = AccountYearInfo(
                self, year_data['year'], year_data['stars'])
            year_info.fill_days_from_collected_data(year_data)
            self.year_infos[year_info.year] = year_info

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
        """
        Convert to JSON. The data are versioned

        >>> AccountInfo.from_collected_data({
        ...     "username": "Test User", "total_stars": 5, "years": {
        ...         2020: {"year": 2020, "stars": 5, "days": {
        ...             1: 2,
        ...             2: 1,
        ...             3: 0,
        ...         }}}}).serialise()
        {'version': 2, 'username': 'Test User', 'total_stars': 5, 'years':
            {'2020': {'year': 2020, 'stars': 5, 'days':
                {'1': {'year': 2020, 'day': 1, 'stars': 2, 'parts':
                    {'a': {'year': 2020, 'day': 1, 'part': 'a', 'has_star':
                        True},
                    'b': {'year': 2020, 'day': 1, 'part': 'b', 'has_star':
                        True}}},
                '2': {'year': 2020, 'day': 2, 'stars': 1, 'parts':
                    {'a': {'year': 2020, 'day': 2, 'part': 'a', 'has_star':
                        True},
                    'b': {'year': 2020, 'day': 2, 'part': 'b', 'has_star':
                        False}}},
                '3': {'year': 2020, 'day': 3, 'stars': 0, 'parts':
                    {'a': {'year': 2020, 'day': 3, 'part': 'a', 'has_star':
                        False},
                    'b': {'year': 2020, 'day': 3, 'part': 'b', 'has_star':
                        False}}}}}}}
        """
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

    def fill_days_from_collected_data(self, year_data):
        """Parse the days information from collected data"""
        for day, stars in year_data['days'].items():
            day_info = AccountDayInfo(self, day, stars)
            day_info.fill_parts()
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
