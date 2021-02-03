from unittest import TestCase

from tests.utils import using_controller


class TestControllerListDays(TestCase):
    def check_output(self, parts_to_create_on_disk, collected_data,
                     expected_output, expected_result, year):
        with using_controller(parts_to_create_on_disk, collected_data) \
                as (controller, _, captured):
            self.assertEqual(controller.list_days(year), expected_result)
        self.assertEqual(captured.getvalue(), expected_output)

    def test_list_with_no_info(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {},
        }, (
            "Could not find 2020 in code nor any stars\n"
        ), False, 2020)

    def test_list_with_one_year_with_no_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 0, "years": {
                2020: {"year": 2020, "stars": 0, "days": {}},
            },
        }, (
            "Could not find 2020 in code nor any stars\n"
        ), False, 2020)

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
            "Could not find 2020 in code, but found 3 stars\n"
        ), False, 2020)

    def test_list_different_year_with_one_year_with_some_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 3, "years": {
                2020: {"year": 2020, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        }, (
            "Could not find 2019 in code nor any stars\n"
        ), False, 2019)

    def test_list_with_one_year_with_all_stars(self):
        self.check_output([], {
            "username": "Test User", "total_stars": 50, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
            },
        }, (
            "Could not find 2020 in code, but found 50 stars\n"
        ), False, 2020)

    def test_list_with_all_stars_and_code(self):
        self.check_output([
            (2020, day, part)
            for part in ['a', 'b']
            for day in range(1, 26)
        ], {
            "username": "Test User", "total_stars": 50, "years": {
                2020: {"year": 2020, "stars": 50, "days": {
                    day: 2
                    for day in range(1, 26)
                }},
            },
        }, (
            "Found 25 days with code in 2020 with 50 stars:\n"
            "  * 25**, 24**, 23**, 22**, 21**, "
            "20**, 19**, 18**, 17**, 16**, 15**, 14**, 13**, 12**, 11**, "
            "10**, 9**, 8**, 7**, 6**, 5**, 4**, 3**, 2**, 1**\n"
        ), True, 2020)

    def test_list_with_some_stars_and_code(self):
        self.check_output([
            (2018, 1, 'a'), (2018, 1, 'b'),
            (2018, 2, 'a'), (2018, 2, 'b'),
            (2018, 3, 'a'),
        ], {
            "username": "Test User", "total_stars": 3, "years": {
                2018: {"year": 2018, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        }, (
            "Found 3 days with code in 2018 with 3 stars:\n"
            "  * 3x!, 2*x, 1**\n"
        ), True, 2018)

    def test_list_with_some_mismatched_stars_and_code(self):
        self.check_output([
            (2018, 1, 'a'), (2018, 1, 'b'),
            (2018, 4, 'a'), (2018, 4, 'b'),
            (2018, 5, 'a'),
        ], {
            "username": "Test User", "total_stars": 3, "years": {
                2018: {"year": 2018, "stars": 3, "days": {
                    1: 2,
                    2: 1,
                    3: 0,
                }},
            },
        }, (
            "Found 3 days with code in 2018 with 3 stars:\n"
            "  * 5x!, 4x!, 1**\n"
        ), True, 2018)
