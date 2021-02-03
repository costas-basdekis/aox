import glob
from typing import List, Optional, Dict, Set
from unittest import TestCase

from aox.model import RepoInfo, CombinedInfo, AccountInfo, CombinedPartInfo
from aox.settings import get_settings
from tests.utils import making_combined_info, make_combined_info


# noinspection DuplicatedCode
class BaseAccountInfoTestCase(TestCase):
    maxDiff = None

    parts_to_create_on_disk: List = NotImplemented
    collected_data: Optional[Dict] = NotImplemented

    has_code: bool = NotImplemented
    years_with_code: Set = NotImplemented
    days_with_code: Set = NotImplemented
    parts_with_code: Set = NotImplemented

    total_stars: int = NotImplemented
    years_with_stars: Dict = NotImplemented
    days_with_stars: Dict = NotImplemented
    parts_with_stars: Set = NotImplemented
    parts_with_status: Dict = NotImplemented

    def setUp(self) -> None:
        if type(self) == BaseAccountInfoTestCase:
            self.skipTest("Base test case")

    def get_combined_info(self):
        for part in self.parts_to_create_on_disk:
            get_settings().challenges_boilerplate.create_part(*part)
        return CombinedInfo\
            .from_repo_and_account_infos(
                RepoInfo.from_roots(),
                AccountInfo.from_collected_data(self.collected_data),
            )

    def test_repo_data(self):
        with making_combined_info(
                self.parts_to_create_on_disk, self.collected_data) \
                as combined_info:
            folder_contents = glob.glob(
                f"{get_settings().challenges_root}/**/*", recursive=True)

            self.assertEqual(combined_info.has_code, self.has_code)
            self.assertTrue(set(combined_info.year_infos).issuperset(
                {2015, 2016, 2017, 2018, 2019, 2020}))

            # Check years with code
            self.assertEqual({
                year_info.year
                for year_info in combined_info.year_infos.values()
                if str(year_info.path) in folder_contents
            }, self.years_with_code)
            self.assertEqual({
                year_info.year
                for year_info in combined_info.year_infos.values()
                if year_info.has_code
            }, self.years_with_code)
            self.assertEqual({
                year_info.year
                for year_info in combined_info.year_infos.values()
                if year_info.path.exists()
            }, self.years_with_code)

            # Check days with code
            self.assertEqual({
                (day_info.year, day_info.day)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                if str(day_info.path) in folder_contents
            }, self.days_with_code)
            self.assertEqual({
                (day_info.year, day_info.day)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                if day_info.has_code
            }, self.days_with_code)
            self.assertEqual({
                (day_info.year, day_info.day)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                if day_info.path.exists()
            }, self.days_with_code)

            # Check parts with code
            self.assertEqual({
                (part_info.year, part_info.day, part_info.part)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                for part_info in day_info.part_infos.values()
                if str(part_info.path) in folder_contents
            }, self.parts_with_code)
            self.assertEqual({
                (part_info.year, part_info.day, part_info.part)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                for part_info in day_info.part_infos.values()
                if part_info.has_code
            }, self.parts_with_code)
            self.assertEqual({
                (part_info.year, part_info.day, part_info.part)
                for year_info in combined_info.year_infos.values()
                for day_info in year_info.day_infos.values()
                for part_info in day_info.part_infos.values()
                if part_info.path.exists()
            }, self.parts_with_code)

            for year, year_info in combined_info.year_infos.items():
                self.assertEqual(year_info.year, year)
                self.assertEqual(
                    set(year_info.day_infos), set(range(1, 26)))
                for day, day_info in year_info.day_infos.items():
                    self.assertEqual(day_info.year_info, year_info)
                    self.assertEqual(day_info.year, year)
                    self.assertEqual(day_info.day, day)
                    self.assertEqual(set(day_info.part_infos), {'a', 'b'})
                    for part, part_info in day_info.part_infos.items():
                        self.assertEqual(part_info.day_info, day_info)
                        self.assertEqual(part_info.year, year)
                        self.assertEqual(part_info.day, day)
                        self.assertEqual(part_info.part, part)

    def test_account_data(self):
        combined_info = make_combined_info(
                self.parts_to_create_on_disk, self.collected_data)

        self.assertEqual(combined_info.total_stars, self.total_stars)

        # Check years with stars
        self.assertEqual({
            year_info.year: year_info.stars
            for year_info in combined_info.year_infos.values()
            if year_info.stars
        }, self.years_with_stars)

        # Check days with stars
        self.assertEqual({
            (day_info.year, day_info.day): day_info.stars
            for year_info in combined_info.year_infos.values()
            for day_info in year_info.day_infos.values()
            if day_info.stars
        }, self.days_with_stars)

        # Check parts with stars
        self.assertEqual({
            (part_info.year, part_info.day, part_info.part)
            for year_info in combined_info.year_infos.values()
            for day_info in year_info.day_infos.values()
            for part_info in day_info.part_infos.values()
            if part_info.has_star
        }, self.parts_with_stars)

        # Check parts by status
        self.assertEqual({
            (part_info.year, part_info.day, part_info.part): part_info.status
            for year_info in combined_info.year_infos.values()
            for day_info in year_info.day_infos.values()
            for part_info in day_info.part_infos.values()
            if part_info.status != part_info.STATUS_DID_NOT_ATTEMPT
        }, self.parts_with_status)


class TestAccountInfoWithNoCodeAndNoAccountInfo(BaseAccountInfoTestCase):
    parts_to_create_on_disk = []
    collected_data = None

    has_code = False
    years_with_code = set()
    days_with_code = set()
    parts_with_code = set()

    total_stars = 0
    years_with_stars = {}
    days_with_stars = {}
    parts_with_stars = set()
    parts_with_status = {}


# noinspection DuplicatedCode
class TestAccountInfoWithSomeCodeAndNoAccountInfo(BaseAccountInfoTestCase):
    parts_to_create_on_disk = [
        (2020, 1, 'b'),
        (2020, 2, 'b'),
        (2020, 3, 'b'),
        (2020, 10, 'b'),
        (2020, 11, 'a'),
        (2019, 1, 'b'),
        (2019, 3, 'a'),
        (2019, 11, 'b'),
    ]
    collected_data = None

    has_code = True
    years_with_code = {2019, 2020}
    days_with_code = {
        (2020, 1), (2020, 2), (2020, 3), (2020, 10), (2020, 11),
        (2019, 1), (2019, 3), (2019, 11),
    }
    parts_with_code = {
        (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'),
        (2020, 2, 'b'), (2020, 3, 'a'), (2020, 3, 'b'),
        (2020, 10, 'a'), (2020, 10, 'b'), (2020, 11, 'a'),
        (2019, 1, 'a'), (2019, 1, 'b'), (2019, 3, 'a'),
        (2019, 11, 'a'), (2019, 11, 'b'),
    }

    total_stars = 0
    years_with_stars = {}
    days_with_stars = {}
    parts_with_stars = set()
    parts_with_status = {}


# noinspection DuplicatedCode
class TestAccountInfoWithNoCodeAndSomeAccountInfo(BaseAccountInfoTestCase):
    parts_to_create_on_disk = []
    collected_data = {
        "username": "Test User",
        "total_stars": 13,
        "years": {
            2020: {
                "year": 2020, "stars": 5,
                "days": {
                    **{day: 0 for day in range(1, 26)},
                    1: 2, 2: 1,
                },
            },
            2018: {
                "year": 2018, "stars": 8,
                "days": {
                    **{day: 0 for day in range(1, 26)},
                    1: 2, 2: 1, 5: 1, 10: 2, 21: 2,
                },
            },
        },
    }

    has_code = False
    years_with_code = set()
    days_with_code = set()
    parts_with_code = set()

    total_stars = 13
    years_with_stars = {2020: 5, 2018: 8}
    days_with_stars = {
        (2020, 1): 2, (2020, 2): 1, (2018, 1): 2, (2018, 2): 1,
        (2018, 5): 1, (2018, 10): 2, (2018, 21): 2,
    }
    parts_with_stars = {
        (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'), (2018, 1, 'a'),
        (2018, 1, 'b'), (2018, 2, 'a'), (2018, 5, 'a'), (2018, 10, 'a'),
        (2018, 10, 'b'), (2018, 21, 'a'), (2018, 21, 'b'),
    }
    parts_with_status = {
        (2020, 1, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2020, 1, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2020, 2, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 1, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 1, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 2, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 5, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 10, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 10, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 21, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 21, 'b'): CombinedPartInfo.STATUS_COMPLETE,
    }


# noinspection DuplicatedCode
class TestAccountInfoWithSomeCodeAndSomeAccountInfo(BaseAccountInfoTestCase):
    parts_to_create_on_disk = [
        (2020, 1, 'b'),
        (2020, 2, 'b'),
        (2020, 3, 'b'),
        (2020, 10, 'b'),
        (2020, 11, 'a'),
        (2019, 1, 'b'),
        (2019, 3, 'a'),
        (2019, 11, 'b'),
    ]
    collected_data = {
        "username": "Test User",
        "total_stars": 13,
        "years": {
            2020: {
                "year": 2020, "stars": 5,
                "days": {
                    **{day: 0 for day in range(1, 26)},
                    1: 2, 2: 1,
                },
            },
            2018: {
                "year": 2018, "stars": 8,
                "days": {
                    **{day: 0 for day in range(1, 26)},
                    1: 2, 2: 1, 5: 1, 10: 2, 21: 2,
                },
            },
        },
    }

    has_code = True
    years_with_code = {2019, 2020}
    days_with_code = {
        (2020, 1), (2020, 2), (2020, 3), (2020, 10), (2020, 11),
        (2019, 1), (2019, 3), (2019, 11),
    }
    parts_with_code = {
        (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'),
        (2020, 2, 'b'), (2020, 3, 'a'), (2020, 3, 'b'),
        (2020, 10, 'a'), (2020, 10, 'b'), (2020, 11, 'a'),
        (2019, 1, 'a'), (2019, 1, 'b'), (2019, 3, 'a'),
        (2019, 11, 'a'), (2019, 11, 'b'),
    }

    total_stars = 13
    years_with_stars = {2020: 5, 2018: 8}
    days_with_stars = {
        (2020, 1): 2, (2020, 2): 1, (2018, 1): 2, (2018, 2): 1,
        (2018, 5): 1, (2018, 10): 2, (2018, 21): 2,
    }
    parts_with_stars = {
        (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'), (2018, 1, 'a'),
        (2018, 1, 'b'), (2018, 2, 'a'), (2018, 5, 'a'), (2018, 10, 'a'),
        (2018, 10, 'b'), (2018, 21, 'a'), (2018, 21, 'b'),
    }
    parts_with_status = {
        (2020, 1, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2020, 1, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2020, 2, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2020, 2, 'b'): CombinedPartInfo.STATUS_FAILED,
        (2020, 3, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2020, 3, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2020, 10, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2020, 10, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2020, 11, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2020, 11, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2019, 1, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2019, 1, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2019, 3, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2019, 3, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2019, 11, 'a'): CombinedPartInfo.STATUS_FAILED,
        (2019, 11, 'b'): CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT,
        (2018, 1, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 1, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 2, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 5, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 10, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 10, 'b'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 21, 'a'): CombinedPartInfo.STATUS_COMPLETE,
        (2018, 21, 'b'): CombinedPartInfo.STATUS_COMPLETE,
    }
