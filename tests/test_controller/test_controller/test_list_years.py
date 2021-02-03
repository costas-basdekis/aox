from unittest import TestCase

from tests.utils import using_controller


# noinspection DuplicatedCode
class TestControllerListYears(TestCase):
    def check_output(self, parts_to_create_on_disk, collected_data,
                     expected_output):
        with using_controller(parts_to_create_on_disk, collected_data) \
                as (controller, _, captured):
            controller.list_years()
        self.assertEqual(captured.getvalue(), expected_output)

    def test_list_with_no_info(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {},
        }, (
            "Found 0 years with code and 0 stars:\n"
        ))

    def test_list_with_one_year_with_no_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {
                2020: {"year": 2020, "stars": 0, "days": {}},
            },
        }, (
            "Found 0 years with code and 0 stars:\n"
        ))

    def test_list_with_one_year_with_some_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 3, "years": {
                2020: {"year": 2020, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        }, (
            "Found 0 years with code and 3 stars:\n"
            "  * 2020: 0 days with code and 3 stars\n"
        ))

    def test_list_with_one_year_with_all_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 50, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
            },
        }, (
            "Found 0 years with code and 50 stars:\n"
            "  * 2020: 0 days with code and 50 stars\n"
        ))

    def test_list_with_multiple_years_with_different_number_of_stars(self):
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
        }, (
            "Found 0 years with code and 105 stars:\n"
            "  * 2020: 0 days with code and 50 stars\n"
            "  * 2019: 0 days with code and 5 stars\n"
            "  * 2018: 0 days with code and 50 stars\n"
            "  * 2016: 0 days with code and 1 stars\n"
        ))

    def test_list_with_multiple_years_with_different_stars_and_code(self):
        self.check_output([
            (2020, day, part)
            for part in ['a', 'b']
            for day in range(1, 26)
        ] + [
            (2018, 1, 'a'), (2018, 1, 'b'),
            (2018, 2, 'a'), (2018, 2, 'b'),
            (2018, 3, 'a'),
        ], {
            "username": "Test User", "total_stars": 53, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
                2018: {"year": 2018, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        }, (
            "Found 2 years with code and 53 stars:\n"
            "  * 2020: 25 days with code and 50 stars\n"
            "  * 2018: 3 days with code and 3 stars\n"
        ))
