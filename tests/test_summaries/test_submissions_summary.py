from unittest import TestCase

from aox.model import CombinedInfo, RepoInfo, AccountInfo
from aox.summary import SubmissionsSummary
from tests.utils import making_combined_info


class TestSubmissionsSummary(TestCase):
    maxDiff = None

    def get_years_links(self, years):
        return "".join(map(self.get_year_links, years))

    def get_year_links(self, year):
        return (
            "\n"
            "[ch-{short_year}]: https://adventofcode.com/{year}\n"
            "[co-{short_year}]: year_{year}\n"
            + "".join(
                (
                    "[ch-{{short_year}}-{day:0>2}]: "
                    "https://adventofcode.com/{{year}}/day/{day}\n"
                    "[co-{{short_year}}-{day:0>2}]: "
                    "year_{{year}}/day_{day:0>2}\n"
                ).format(day=day)
                for day in range(1, 26)
            )
        ).format(year=year, short_year=str(year)[-2:])

    def test_generate_with_no_info(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 0, "years": {},
            }),
        )
        self.assertEqual(SubmissionsSummary().generate(combined_info), (
            "\n\n"
            "|       |\n"
            "|  ---: |\n"
            "|       |\n"
            "|       |\n"
            "|  1    |\n"
            "|  2    |\n"
            "|  3    |\n"
            "|  4    |\n"
            "|  5    |\n"
            "|  6    |\n"
            "|  7    |\n"
            "|  8    |\n"
            "|  9    |\n"
            "| 10    |\n"
            "| 11    |\n"
            "| 12    |\n"
            "| 13    |\n"
            "| 14    |\n"
            "| 15    |\n"
            "| 16    |\n"
            "| 17    |\n"
            "| 18    |\n"
            "| 19    |\n"
            "| 20    |\n"
            "| 21    |\n"
            "| 22    |\n"
            "| 23    |\n"
            "| 24    |\n"
            "| 25    |\n"
            "\n"
            "\n"
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
        self.assertEqual(SubmissionsSummary().generate(combined_info), (
            "\n\n"
            "|       |\n"
            "|  ---: |\n"
            "|       |\n"
            "|       |\n"
            "|  1    |\n"
            "|  2    |\n"
            "|  3    |\n"
            "|  4    |\n"
            "|  5    |\n"
            "|  6    |\n"
            "|  7    |\n"
            "|  8    |\n"
            "|  9    |\n"
            "| 10    |\n"
            "| 11    |\n"
            "| 12    |\n"
            "| 13    |\n"
            "| 14    |\n"
            "| 15    |\n"
            "| 16    |\n"
            "| 17    |\n"
            "| 18    |\n"
            "| 19    |\n"
            "| 20    |\n"
            "| 21    |\n"
            "| 22    |\n"
            "| 23    |\n"
            "| 24    |\n"
            "| 25    |\n"
            "\n"
            "\n"
            "\n"
        ))

    def test_generate_with_one_year_with_some_stars(self):
        combined_info = CombinedInfo.from_repo_and_account_infos(
            RepoInfo.from_roots([]),
            AccountInfo.from_collected_data({
                "username": "Test User", "total_stars": 3, "years": {
                    2020: {"year": 2020, "stars": 3, "days": {
                        1: 2,
                        2: 1,
                        3: 0,
                    }},
                },
            }),
        )
        self.assertEqual(SubmissionsSummary().generate(combined_info), (
            "\n\n"
            "|       | 2020                                     |\n"
            "|  ---: | :---:                                    |\n"
            "|       | Code &             [Challenges][ch-20]   |\n"
            "|       | 3 :star: / 0 :x: / 0 :grey_exclamation:  |\n"
            "|  1    | Code :star: :star: [Challenge][ch-20-01] |\n"
            "|  2    | Code :star:        [Challenge][ch-20-02] |\n"
            "|  3    | Code               [Challenge][ch-20-03] |\n"
            "|  4    | Code               [Challenge][ch-20-04] |\n"
            "|  5    | Code               [Challenge][ch-20-05] |\n"
            "|  6    | Code               [Challenge][ch-20-06] |\n"
            "|  7    | Code               [Challenge][ch-20-07] |\n"
            "|  8    | Code               [Challenge][ch-20-08] |\n"
            "|  9    | Code               [Challenge][ch-20-09] |\n"
            "| 10    | Code               [Challenge][ch-20-10] |\n"
            "| 11    | Code               [Challenge][ch-20-11] |\n"
            "| 12    | Code               [Challenge][ch-20-12] |\n"
            "| 13    | Code               [Challenge][ch-20-13] |\n"
            "| 14    | Code               [Challenge][ch-20-14] |\n"
            "| 15    | Code               [Challenge][ch-20-15] |\n"
            "| 16    | Code               [Challenge][ch-20-16] |\n"
            "| 17    | Code               [Challenge][ch-20-17] |\n"
            "| 18    | Code               [Challenge][ch-20-18] |\n"
            "| 19    | Code               [Challenge][ch-20-19] |\n"
            "| 20    | Code               [Challenge][ch-20-20] |\n"
            "| 21    | Code               [Challenge][ch-20-21] |\n"
            "| 22    | Code               [Challenge][ch-20-22] |\n"
            "| 23    | Code               [Challenge][ch-20-23] |\n"
            "| 24    | Code               [Challenge][ch-20-24] |\n"
            "| 25    | Code               [Challenge][ch-20-25] |\n"
            + self.get_years_links([2020]) +
            "\n"
        ))

    def test_generate_with_one_year_with_some_stars_and_code(self):
        with making_combined_info(
            [
                (2020, 1, 'a'), (2020, 1, 'b'),
                (2020, 2, 'a'), (2020, 2, 'b'),
                (2020, 3, 'a'),
            ],
            {
                "username": "Test User", "total_stars": 3, "years": {
                    2020: {"year": 2020, "stars": 3, "days": {
                        1: 2,
                        2: 1,
                        3: 0,
                    }},
                },
            },
        ) as combined_info:
            self.assertEqual(SubmissionsSummary().generate(combined_info), (
                "\n\n"
                "|       | 2020                                                             |\n"
                "|  ---: | :---:                                                            |\n"
                "|       | [Code][co-20]    &                         [Challenges][ch-20]   |\n"
                "|       | 3 :star: / 2 :x: / 1 :grey_exclamation:                          |\n"
                "|  1    | [Code][co-20-01] :star: :star:             [Challenge][ch-20-01] |\n"
                "|  2    | [Code][co-20-02] :star: :x:                [Challenge][ch-20-02] |\n"
                "|  3    | [Code][co-20-03] :x:    :grey_exclamation: [Challenge][ch-20-03] |\n"
                "|  4    | Code                                       [Challenge][ch-20-04] |\n"
                "|  5    | Code                                       [Challenge][ch-20-05] |\n"
                "|  6    | Code                                       [Challenge][ch-20-06] |\n"
                "|  7    | Code                                       [Challenge][ch-20-07] |\n"
                "|  8    | Code                                       [Challenge][ch-20-08] |\n"
                "|  9    | Code                                       [Challenge][ch-20-09] |\n"
                "| 10    | Code                                       [Challenge][ch-20-10] |\n"
                "| 11    | Code                                       [Challenge][ch-20-11] |\n"
                "| 12    | Code                                       [Challenge][ch-20-12] |\n"
                "| 13    | Code                                       [Challenge][ch-20-13] |\n"
                "| 14    | Code                                       [Challenge][ch-20-14] |\n"
                "| 15    | Code                                       [Challenge][ch-20-15] |\n"
                "| 16    | Code                                       [Challenge][ch-20-16] |\n"
                "| 17    | Code                                       [Challenge][ch-20-17] |\n"
                "| 18    | Code                                       [Challenge][ch-20-18] |\n"
                "| 19    | Code                                       [Challenge][ch-20-19] |\n"
                "| 20    | Code                                       [Challenge][ch-20-20] |\n"
                "| 21    | Code                                       [Challenge][ch-20-21] |\n"
                "| 22    | Code                                       [Challenge][ch-20-22] |\n"
                "| 23    | Code                                       [Challenge][ch-20-23] |\n"
                "| 24    | Code                                       [Challenge][ch-20-24] |\n"
                "| 25    | Code                                       [Challenge][ch-20-25] |\n"
                + self.get_years_links([2020]) +
                "\n"
            ))

    def test_generate_with_one_year_with_all_stars_and_code(self):
        with making_combined_info(
            [
                (2020, day, part)
                for part in ['a', 'b']
                for day in range(1, 26)
            ],
            {
                "username": "Test User", "total_stars": 50, "years": {
                    2020: {"year": 2020, "stars": 50, "days": {
                        day: 2
                        for day in range(1, 26)
                    }},
                },
            },
        ) as combined_info:
            self.assertEqual(SubmissionsSummary().generate(combined_info), (
                "\n\n"
                "|       | 2020                                                 |\n"
                "|  ---: | :---:                                                |\n"
                "|       | [Code][co-20]    &             [Challenges][ch-20]   |\n"
                "|       | 50 :star: :star:                                     |\n"
                "|  1    | [Code][co-20-01] :star: :star: [Challenge][ch-20-01] |\n"
                "|  2    | [Code][co-20-02] :star: :star: [Challenge][ch-20-02] |\n"
                "|  3    | [Code][co-20-03] :star: :star: [Challenge][ch-20-03] |\n"
                "|  4    | [Code][co-20-04] :star: :star: [Challenge][ch-20-04] |\n"
                "|  5    | [Code][co-20-05] :star: :star: [Challenge][ch-20-05] |\n"
                "|  6    | [Code][co-20-06] :star: :star: [Challenge][ch-20-06] |\n"
                "|  7    | [Code][co-20-07] :star: :star: [Challenge][ch-20-07] |\n"
                "|  8    | [Code][co-20-08] :star: :star: [Challenge][ch-20-08] |\n"
                "|  9    | [Code][co-20-09] :star: :star: [Challenge][ch-20-09] |\n"
                "| 10    | [Code][co-20-10] :star: :star: [Challenge][ch-20-10] |\n"
                "| 11    | [Code][co-20-11] :star: :star: [Challenge][ch-20-11] |\n"
                "| 12    | [Code][co-20-12] :star: :star: [Challenge][ch-20-12] |\n"
                "| 13    | [Code][co-20-13] :star: :star: [Challenge][ch-20-13] |\n"
                "| 14    | [Code][co-20-14] :star: :star: [Challenge][ch-20-14] |\n"
                "| 15    | [Code][co-20-15] :star: :star: [Challenge][ch-20-15] |\n"
                "| 16    | [Code][co-20-16] :star: :star: [Challenge][ch-20-16] |\n"
                "| 17    | [Code][co-20-17] :star: :star: [Challenge][ch-20-17] |\n"
                "| 18    | [Code][co-20-18] :star: :star: [Challenge][ch-20-18] |\n"
                "| 19    | [Code][co-20-19] :star: :star: [Challenge][ch-20-19] |\n"
                "| 20    | [Code][co-20-20] :star: :star: [Challenge][ch-20-20] |\n"
                "| 21    | [Code][co-20-21] :star: :star: [Challenge][ch-20-21] |\n"
                "| 22    | [Code][co-20-22] :star: :star: [Challenge][ch-20-22] |\n"
                "| 23    | [Code][co-20-23] :star: :star: [Challenge][ch-20-23] |\n"
                "| 24    | [Code][co-20-24] :star: :star: [Challenge][ch-20-24] |\n"
                "| 25    | [Code][co-20-25] :star: :star: [Challenge][ch-20-25] |\n"
                + self.get_years_links([2020]) +
                "\n"
            ))

    def test_generate_with_multiple_years_with_different_stars_and_code(self):
        with making_combined_info(
            [
                (2020, day, part)
                for part in ['a', 'b']
                for day in range(1, 26)
            ] + [
                (2018, 1, 'a'), (2018, 1, 'b'),
                (2018, 2, 'a'), (2018, 2, 'b'),
                (2018, 3, 'a'),
            ],
            {
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
            },
        ) as combined_info:
            self.assertEqual(SubmissionsSummary().generate(combined_info), (
                "\n\n"
                "|       | 2020                                                 | 2018                                                             |\n"
                "|  ---: | :---:                                                | :---:                                                            |\n"
                "|       | [Code][co-20]    &             [Challenges][ch-20]   | [Code][co-18]    &                         [Challenges][ch-18]   |\n"
                "|       | 50 :star: :star:                                     | 3 :star: / 2 :x: / 1 :grey_exclamation:                          |\n"
                "|  1    | [Code][co-20-01] :star: :star: [Challenge][ch-20-01] | [Code][co-18-01] :star: :star:             [Challenge][ch-18-01] |\n"
                "|  2    | [Code][co-20-02] :star: :star: [Challenge][ch-20-02] | [Code][co-18-02] :star: :x:                [Challenge][ch-18-02] |\n"
                "|  3    | [Code][co-20-03] :star: :star: [Challenge][ch-20-03] | [Code][co-18-03] :x:    :grey_exclamation: [Challenge][ch-18-03] |\n"
                "|  4    | [Code][co-20-04] :star: :star: [Challenge][ch-20-04] | Code                                       [Challenge][ch-18-04] |\n"
                "|  5    | [Code][co-20-05] :star: :star: [Challenge][ch-20-05] | Code                                       [Challenge][ch-18-05] |\n"
                "|  6    | [Code][co-20-06] :star: :star: [Challenge][ch-20-06] | Code                                       [Challenge][ch-18-06] |\n"
                "|  7    | [Code][co-20-07] :star: :star: [Challenge][ch-20-07] | Code                                       [Challenge][ch-18-07] |\n"
                "|  8    | [Code][co-20-08] :star: :star: [Challenge][ch-20-08] | Code                                       [Challenge][ch-18-08] |\n"
                "|  9    | [Code][co-20-09] :star: :star: [Challenge][ch-20-09] | Code                                       [Challenge][ch-18-09] |\n"
                "| 10    | [Code][co-20-10] :star: :star: [Challenge][ch-20-10] | Code                                       [Challenge][ch-18-10] |\n"
                "| 11    | [Code][co-20-11] :star: :star: [Challenge][ch-20-11] | Code                                       [Challenge][ch-18-11] |\n"
                "| 12    | [Code][co-20-12] :star: :star: [Challenge][ch-20-12] | Code                                       [Challenge][ch-18-12] |\n"
                "| 13    | [Code][co-20-13] :star: :star: [Challenge][ch-20-13] | Code                                       [Challenge][ch-18-13] |\n"
                "| 14    | [Code][co-20-14] :star: :star: [Challenge][ch-20-14] | Code                                       [Challenge][ch-18-14] |\n"
                "| 15    | [Code][co-20-15] :star: :star: [Challenge][ch-20-15] | Code                                       [Challenge][ch-18-15] |\n"
                "| 16    | [Code][co-20-16] :star: :star: [Challenge][ch-20-16] | Code                                       [Challenge][ch-18-16] |\n"
                "| 17    | [Code][co-20-17] :star: :star: [Challenge][ch-20-17] | Code                                       [Challenge][ch-18-17] |\n"
                "| 18    | [Code][co-20-18] :star: :star: [Challenge][ch-20-18] | Code                                       [Challenge][ch-18-18] |\n"
                "| 19    | [Code][co-20-19] :star: :star: [Challenge][ch-20-19] | Code                                       [Challenge][ch-18-19] |\n"
                "| 20    | [Code][co-20-20] :star: :star: [Challenge][ch-20-20] | Code                                       [Challenge][ch-18-20] |\n"
                "| 21    | [Code][co-20-21] :star: :star: [Challenge][ch-20-21] | Code                                       [Challenge][ch-18-21] |\n"
                "| 22    | [Code][co-20-22] :star: :star: [Challenge][ch-20-22] | Code                                       [Challenge][ch-18-22] |\n"
                "| 23    | [Code][co-20-23] :star: :star: [Challenge][ch-20-23] | Code                                       [Challenge][ch-18-23] |\n"
                "| 24    | [Code][co-20-24] :star: :star: [Challenge][ch-20-24] | Code                                       [Challenge][ch-18-24] |\n"
                "| 25    | [Code][co-20-25] :star: :star: [Challenge][ch-20-25] | Code                                       [Challenge][ch-18-25] |\n"
                + self.get_years_links([2020, 2018]) +
                "\n"
            ))
