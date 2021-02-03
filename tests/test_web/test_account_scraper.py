from unittest import TestCase

import responses

from aox.utils import get_current_directory
from aox.web import AccountScraper, WebAoc

current_directory = get_current_directory()
web_fixtures = current_directory.joinpath('web_fixtures')


class TestAccountScraperScraper(TestCase):
    @responses.activate
    def test_collect_data(self):
        responses.add(
            responses.GET, 'https://adventofcode.com/events',
            body=web_fixtures.joinpath('events.html').read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET, 'https://adventofcode.com/2020',
            body=web_fixtures.joinpath('2020.html').read_bytes(),
            status=200,
        )

        scraper = AccountScraper(WebAoc('test-session'))
        # noinspection DuplicatedCode
        self.assertEqual(scraper.collect_data(), {
            "username": "Test User",
            "total_stars": 39,
            "years": {
                2020: {
                    "year": 2020,
                    "stars": 39,
                    "days": {
                        1: 2,
                        2: 2,
                        3: 2,
                        4: 2,
                        5: 2,
                        6: 2,
                        7: 2,
                        8: 2,
                        9: 2,
                        10: 2,
                        11: 2,
                        12: 2,
                        13: 2,
                        14: 1,
                        15: 2,
                        16: 2,
                        17: 2,
                        18: 0,
                        19: 2,
                        20: 2,
                        21: 1,
                        22: 0,
                        23: 0,
                        24: 0,
                        25: 0,
                    },
                }
            },
        })

    @responses.activate
    def test_collect_year(self):
        responses.add(
            responses.GET, 'https://adventofcode.com/2020',
            body=web_fixtures.joinpath('2020.html').read_bytes(),
            status=200,
        )

        scraper = AccountScraper(WebAoc('test-session'))
        # noinspection DuplicatedCode
        self.assertEqual(scraper.collect_year(2020, 39), {
            "year": 2020,
            "stars": 39,
            "days": {
                1: 2,
                2: 2,
                3: 2,
                4: 2,
                5: 2,
                6: 2,
                7: 2,
                8: 2,
                9: 2,
                10: 2,
                11: 2,
                12: 2,
                13: 2,
                14: 1,
                15: 2,
                16: 2,
                17: 2,
                18: 0,
                19: 2,
                20: 2,
                21: 1,
                22: 0,
                23: 0,
                24: 0,
                25: 0,
            },
        })
