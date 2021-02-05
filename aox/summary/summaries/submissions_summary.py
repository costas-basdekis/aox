from aox import utils
from aox.model import CombinedDayInfo, CombinedYearInfo, CombinedPartInfo, \
    CombinedInfo
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
        CombinedPartInfo.STATUS_COMPLETE: ':star:',
        CombinedPartInfo.STATUS_FAILED: ':x:',
        CombinedPartInfo.STATUS_DID_NOT_ATTEMPT: '',
        CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT:
        ':grey_exclamation:',
    }

    def generate(self, combined_info: CombinedInfo):
        table = self.get_table(combined_info)
        link_definitions = self.get_link_definitions(combined_info)

        return f"\n\n{table}\n\n{link_definitions}\n\n"

    def get_table(self, combined_info):
        years = sorted((
            year
            for year, year_info in combined_info.year_infos.items()
            if year_info.has_code or year_info.stars
        ), reverse=True)
        headers = ('',) + tuple(map(str, years))
        dividers = (' ---:',) + (':---:',) * len(years)
        year_stars = ('',) + tuple(
            self.get_submission_year_stars_text(combined_info.year_infos[year])
            for year in years
        )
        # noinspection PyTypeChecker
        year_links_tuples = [('',)] + [
            (
                (
                    f"[Code][{self.get_code_year_link_name(year)}]"
                    if year_info.has_code else
                    'Code'
                ),
                '&',
                '',
                f"[Challenges][ch-{str(year)[-2:]}]",
            )
            for year in years
            for year_info in (combined_info.year_infos[year],)
        ]
        # noinspection PyTypeChecker
        day_links_tuples_list = [
            [(f"{day: >2}",)] + [
                self.get_submission_year_day_stars_tuple(
                    combined_info.year_infos[year].day_infos[day])
                for year in years
            ]
            for day in range(1, 26)
        ]

        year_links, *day_links_list = \
            utils.simplify_divided_rows(
                [year_links_tuples] + day_links_tuples_list)

        table_rows = [
            headers,
            dividers,
            year_links,
            year_stars,
        ] + day_links_list

        return utils.join_rows(table_rows)

    def get_link_definitions(self, combined_info: CombinedInfo):
        years = sorted((
            year
            for year, year_info in combined_info.year_infos.items()
            if year_info.has_code or year_info.stars
        ), reverse=True)

        return "\n\n".join(
            "\n".join([
                f"[{self.get_challenge_year_link_name(year)}]: "
                f"{year_info.get_year_url()}",
                f"[{self.get_code_year_link_name(year)}]: "
                f"{year_info.relative_path}",
            ] + sum((
                [
                    f"[{self.get_challenge_day_link_name(year, day)}]: "
                    f"{day_info.get_day_url()}",
                    f"[{self.get_code_day_link_name(year, day)}]: "
                    f"{day_info.relative_path}",
                ]
                for day, day_info in (
                    (day, year_info.get_day(day))
                    for day in range(1, 26)
                )
            ), []))
            for year, year_info in (
                (year, combined_info.get_year(year))
                for year in years
            )
        )

    def get_submission_year_stars_text(
            self, year_info: CombinedYearInfo):
        if year_info.stars == 50:
            return f"50 :star: :star:"

        return "{} :star: / {} :x: / {} :grey_exclamation:".format(
            year_info.stars,
            year_info.counts_by_part_status[CombinedPartInfo.STATUS_FAILED],
            year_info.counts_by_part_status[
                CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT],
        )

    def get_submission_year_day_stars_tuple(self, day_info: CombinedDayInfo):
        return (
            (
                f"[Code]"
                f"[{self.get_code_day_link_name(day_info.year, day_info.day)}]"
                if day_info.has_code else
                'Code'
            ),
            self.PART_STATUS_EMOJI_MAP[day_info.part_infos["a"].status],
            self.PART_STATUS_EMOJI_MAP[day_info.part_infos["b"].status],
            f"[Challenge]["
            f"{self.get_challenge_day_link_name(day_info.year, day_info.day)}]",
        )

    def get_code_year_link_name(self, year):
        """
        >>> SubmissionsSummary().get_code_year_link_name(2019)
        'co-19'
        """
        return f"co-{str(year)[-2:]}"

    def get_code_day_link_name(self, year, day):
        """
        >>> SubmissionsSummary().get_code_day_link_name(2019, 5)
        'co-19-05'
        >>> SubmissionsSummary().get_code_day_link_name(2019, 15)
        'co-19-15'
        """
        return f"co-{str(year)[-2:]}-{day:0>2}"

    def get_challenge_year_link_name(self, year):
        """
        >>> SubmissionsSummary().get_challenge_year_link_name(2019)
        'ch-19'
        """
        return f"ch-{str(year)[-2:]}"

    def get_challenge_day_link_name(self, year, day):
        """
        >>> SubmissionsSummary().get_challenge_day_link_name(2019, 5)
        'ch-19-05'
        >>> SubmissionsSummary().get_challenge_day_link_name(2019, 15)
        'ch-19-15'
        """
        return f"ch-{str(year)[-2:]}-{day:0>2}"
