from aox import utils
from aox.summary.base_summary import BaseSummary, summary_registry


__all__ = ['SubmissionsSummary']


PART_STATUS_COMPLETE = 'complete'
PART_STATUS_FAILED = 'failed'
PART_STATUS_DID_NOT_ATTEMPT = 'did-not-attempt'
PART_STATUS_COULD_NOT_ATTEMPT = 'could-not-attempt'


@summary_registry.register
class SubmissionsSummary(BaseSummary):
    """
    Show the stars for every challenge, along with links to the code and the AOC
    challenge webpage, in a year-horizontal, day-vertical table.
    """
    marker_prefix = "submissions"

    PART_STATUS_EMOJI_MAP = {
        PART_STATUS_COMPLETE: ':star:',
        PART_STATUS_FAILED: ':x:',
        PART_STATUS_DID_NOT_ATTEMPT: '',
        PART_STATUS_COULD_NOT_ATTEMPT: ':grey_exclamation:',
    }

    def generate(self, combined_data):
        years = sorted(combined_data["years"], reverse=True)
        headers = ('',) + tuple(years)
        dividers = (' ---:',) + (':---:',) * len(years)
        year_stars = ('',) + tuple(
            self.get_submission_year_stars_text(combined_data["years"][year])
            for year in years
        )
        year_links_tuples = [
            (
                (
                    f"[Code][co-{str(year)[-2:]}]"
                    if year_data["has_code"] else
                    'Code'
                ),
                '&',
                '',
                f"[Challenges][ch-{year[-2:]}]",
            )
            for year in years
            for year_data in (combined_data["years"][year],)
        ]
        day_links_tuples_list = [
            [
                self.get_submission_year_day_stars_tuple(
                    combined_data["years"][year]["days"][str(day)])
                for year in years
            ]
            for day in range(1, 26)
        ]

        list_of_tuples_to_align = [
            list(column)
            for column
            in zip(*([year_links_tuples] + day_links_tuples_list))
        ]
        list_of_aligned_tuples = [
            utils.align_rows(column)
            for column in list_of_tuples_to_align
        ]

        aligned_year_links_tuples = [
            _tuple[0]
            for _tuple in list_of_aligned_tuples
        ]
        aligned_day_links_tuples_list = list(zip(*(
            _tuple[1:]
            for _tuple in list_of_aligned_tuples
        )))

        year_links = ('',) + tuple(map(' '.join, aligned_year_links_tuples))
        day_links_list = [
            (f"{day: >2}",) + tuple(map(' '.join, day_links_tuples))
            for day, day_links_tuples
            in zip(range(1, 26), aligned_day_links_tuples_list)
        ]

        table_rows = [
            headers,
            dividers,
            year_links,
            year_stars,
        ] + day_links_list

        aligned_table_rows = utils.align_rows(table_rows)

        table = "\n".join(
            f"| {' | '.join(row)} |"
            for row in aligned_table_rows
        )

        link_definitions = "\n\n".join(
            "\n".join([
                f"[ch-{year[-2:]}]: https://adventofcode.com/{year}",
                f"[co-{year[-2:]}]: year_{year}",
            ] + sum((
                [
                    f"[ch-{year[-2:]}-{day:0>2}]: "
                    f"https://adventofcode.com/{year}/day/{day}",
                    f"[co-{year[-2:]}-{day:0>2}]: year_{year}/day_{day:0>2}",
                ]
                for day in range(1, 26)
            ), []))
            for year in years
        )

        return f"\n\n{table}\n\n{link_definitions}\n\n"

    def get_submission_year_stars_text(self, year_data):
        if year_data["stars"] == 50:
            return f"50 :star: :star:"

        return "{} :star: / {} :x: / {} :grey_exclamation:".format(
            year_data["stars"],
            year_data["by_part_status"][PART_STATUS_FAILED],
            year_data["by_part_status"][PART_STATUS_COULD_NOT_ATTEMPT],
        )

    def get_submission_year_day_stars_tuple(self, day_data):
        year = day_data["year"]
        day = day_data["day"]
        has_part_a = day_data["parts"]["a"]["has_code"]
        return (
            (
                f"[Code][co-{year[-2:]}-{day}]"
                if has_part_a else
                'Code'
            ),
            self.PART_STATUS_EMOJI_MAP[day_data["parts"]["a"]["status"]],
            self.PART_STATUS_EMOJI_MAP[day_data["parts"]["b"]["status"]],
            f"[Challenge][ch-{year[-2:]}-{day}]",
        )
