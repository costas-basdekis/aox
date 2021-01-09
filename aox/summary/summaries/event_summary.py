from aox.summary.base_summary import BaseSummary, summary_registry


__all__ = ['EventSummary']


@summary_registry.register
class EventSummary(BaseSummary):
    """
    Show the stars for every year, in a horizontal table (columns are years)
    """
    marker_prefix = "event-summary"

    def generate(self, combined_data):
        headers = ['Total'] + sorted(combined_data["years"], reverse=True)
        return "\n\n{}\n{}\n{}\n\n".format(
            f"| {' | '.join(headers)} |",
            f"| {' | '.join(['---'] * len(headers))} |",
            "| {} |".format(" | ".join(
                self.get_header(combined_data, header)
                for header in headers
            )),
        )

    def get_header(self, combined_data, header):
        if header == 'Total':
            stars = combined_data["total_stars"]
        else:
            stars = combined_data["years"][header]["stars"]

        if header != 'Total' and stars == 50:
            emojis = ':star: :star:'
        else:
            emojis = ':star:'

        return f"{stars} {emojis}"
