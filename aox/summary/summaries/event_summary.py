from aox.model import CombinedInfo
from aox.summary.base_summary import BaseSummary, summary_registry


__all__ = ['EventSummary']


@summary_registry.register
class EventSummary(BaseSummary):
    """
    Show the stars for every year, in a horizontal table (columns are years)
    """
    marker_prefix = "event-summary"

    def generate(self, combined_info: CombinedInfo):
        headers = (
            ['Total']
            + list(map(str, sorted((
                year
                for year, year_info in combined_info.year_infos.items()
                if year_info.has_code or year_info.stars
            ), reverse=True)))
        )
        return "\n\n{}\n{}\n{}\n\n".format(
            f"| {' | '.join(headers)} |",
            f"| {' | '.join(['---'] * len(headers))} |",
            "| {} |".format(" | ".join(
                self.get_header(combined_info, header)
                for header in headers
            )),
        )

    def get_header(self, combined_info: CombinedInfo, header):
        if header == 'Total':
            stars = combined_info.total_stars
        else:
            stars = combined_info.year_infos[int(header)].stars

        if header != 'Total' and stars == 50:
            emojis = ':star: :star:'
        else:
            emojis = ':star:'

        return f"{stars} {emojis}"
