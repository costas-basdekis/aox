from unittest import TestCase

from aox.model import CombinedInfo, RepoInfo, AccountInfo
from aox.summary import EventSummary


class TestEventSummary(TestCase):
    def test_generate_with_no_info(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 0, "years": {},
            }),
        )
        self.assertEqual(EventSummary().generate(combined_info), (
            "\n\n"
            "| Total |\n"
            "| --- |\n"
            "| 0 :star: |\n"
            "\n"
        ))

    def test_generate_with_one_year_with_no_stars(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 0, "years": {
                    2020: {"year": 2020, "stars": 0, "days": {}},
                },
            }),
        )
        self.assertEqual(EventSummary().generate(combined_info), (
            "\n\n"
            "| Total |\n"
            "| --- |\n"
            "| 0 :star: |\n"
            "\n"
        ))

    def test_generate_with_one_year_with_some_stars(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 5, "years": {
                    2020: {"year": 2020, "stars": 5, "days": {
                        1: 2,
                        2: 1,
                        3: 0,
                    }},
                },
            }),
        )
        self.assertEqual(EventSummary().generate(combined_info), (
            "\n\n"
            "| Total | 2020 |\n"
            "| --- | --- |\n"
            "| 5 :star: | 5 :star: |\n"
            "\n"
        ))

    def test_generate_with_one_year_with_all_stars(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 50, "years": {
                    2020: {"year": 2020, "stars": 50, "days": {
                        day: 2
                        for day in range(1, 26)
                    }},
                },
            }),
        )
        self.assertEqual(EventSummary().generate(combined_info), (
            "\n\n"
            "| Total | 2020 |\n"
            "| --- | --- |\n"
            "| 50 :star: | 50 :star: :star: |\n"
            "\n"
        ))

    def test_generate_with_multiple_years_with_different_number_of_stars(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
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
            }),
        )
        self.assertEqual(EventSummary().generate(combined_info), (
            "\n\n"
            "| Total | 2020 | 2019 | 2018 | 2016 |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| 105 :star: | 50 :star: :star: | 5 :star: | 50 :star: :star: "
            "| 1 :star: |\n"
            "\n"
        ))
