from aox import utils, combined_discovery
from aox.summary.base_summary import BaseSummary, summary_registry


__all__ = ['SubmissionsSummary']


@summary_registry.register
class SubmissionsSummary(BaseSummary):
    """
    Show the stars for every challenge, along with links to the code and the AOC
    challenge webpage, in a year-horizontal, day-vertical table.
    """
    marker_prefix = "submissions"

    PART_STATUS_EMOJI_MAP = {
        combined_discovery.CombinedPartInfo.STATUS_COMPLETE: ':star:',
        combined_discovery.CombinedPartInfo.STATUS_FAILED: ':x:',
        combined_discovery.CombinedPartInfo.STATUS_DID_NOT_ATTEMPT: '',
        combined_discovery.CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT:
        ':grey_exclamation:',
    }

    def generate(self, combined_data: combined_discovery.CombinedInfo):
        years = sorted((
            year
            for year, year_info in combined_data.year_infos.items()
            if year_info.days_with_code or year_info.stars
        ), reverse=True)
        headers = ('',) + tuple(map(str, years))
        dividers = (' ---:',) + (':---:',) * len(years)
        year_stars = ('',) + tuple(
            self.get_submission_year_stars_text(combined_data.year_infos[year])
            for year in years
        )
        year_links_tuples = [
            (
                (
                    f"[Code][co-{str(year)[-2:]}]"
                    if year_info.days_with_code else
                    'Code'
                ),
                '&',
                '',
                f"[Challenges][ch-{str(year)[-2:]}]",
            )
            for year in years
            for year_info in (combined_data.year_infos[year],)
        ]
        day_links_tuples_list = [
            [
                self.get_submission_year_day_stars_tuple(
                    combined_data.year_infos[year].day_infos[day])
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
                f"[ch-{str(year)[-2:]}]: https://adventofcode.com/{year}",
                f"[co-{str(year)[-2:]}]: year_{year}",
            ] + sum((
                [
                    f"[ch-{str(year)[-2:]}-{day:0>2}]: "
                    f"https://adventofcode.com/{year}/day/{day}",
                    f"[co-{str(year)[-2:]}-{day:0>2}]: "
                    f"year_{year}/day_{day:0>2}",
                ]
                for day in range(1, 26)
            ), []))
            for year in years
        )

        return f"\n\n{table}\n\n{link_definitions}\n\n"

    def get_submission_year_stars_text(
            self, year_info: combined_discovery.CombinedYearInfo):
        if year_info.stars == 50:
            return f"50 :star: :star:"

        return "{} :star: / {} :x: / {} :grey_exclamation:".format(
            year_info.stars,
            year_info.counts_by_part_status[
                combined_discovery.CombinedPartInfo.STATUS_FAILED],
            year_info.counts_by_part_status[
                combined_discovery.CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT],
        )

    def get_submission_year_day_stars_tuple(
            self, day_info: combined_discovery.CombinedDayInfo):
        return (
            (
                f"[Code][co-{str(day_info.year)[-2:]}-{day_info.day:0>2}]"
                if day_info.part_infos["a"].has_code else
                'Code'
            ),
            self.PART_STATUS_EMOJI_MAP[day_info.part_infos["a"].status],
            self.PART_STATUS_EMOJI_MAP[day_info.part_infos["b"].status],
            f"[Challenge][ch-{str(day_info.year)[-2:]}-{day_info.day:0>2}]",
        )
