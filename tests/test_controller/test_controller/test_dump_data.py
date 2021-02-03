import json
from unittest import TestCase

from tests.utils import using_controller


# noinspection DuplicatedCode
class TestControllerDumpData(TestCase):
    maxDiff = None

    def check_output(self, parts_to_create_on_disk, collected_data):
        with using_controller(parts_to_create_on_disk, collected_data) \
                as (controller, combined_info, captured):
            self.assertTrue(controller.dump_data())
            expected = combined_info.serialise()
        dump = captured.getvalue()
        try:
            loaded = json.loads(dump)
        except json.decoder.JSONDecodeError:
            raise Exception(f"Could not parse {dump}")
        self.assertEqual(loaded, expected)

    def test_dump_with_no_info(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {},
        })

    def test_dump_with_one_year_with_no_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {
                2020: {"year": 2020, "stars": 0, "days": {}},
            },
        })

    def test_dump_with_one_year_with_some_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 3, "years": {
                2020: {"year": 2020, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        })

    def test_dump_with_one_year_with_all_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 50, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
            },
        })

    def test_dump_with_multiple_years_with_different_number_of_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 105, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
                2019: {"year": 2019, "stars": 5, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
                2018: {"year": 2018, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
                2017: {"year": 2017, "stars": 0, "days": {}},
                2016: {"year": 2016, "stars": 1, "days": {
                    1: 1,
                }},
            },
        })
