__all__ = ['align_rows']


def align_rows(rows):
    """
    Visually align rows in the source text of an ASCII table.

    This doesn't how the markup gets displayed in HTML, only in the source form.
    """
    row_sizes = set(map(len, rows))
    if len(row_sizes) != 1:
        raise Exception(
            f"Expected rows of equal size but got multiple sizes: "
            f"{', '.join(map(str, sorted(row_sizes)))}")
    column_lengths = tuple(
        max(map(len, column))
        for column in zip(*rows)
    )
    column_formats = tuple(
        f"{{: <{column_length}}}"
        for column_length in column_lengths
    )

    return [
        tuple(
            _format.format(cell)
            for _format, cell in zip(column_formats, row)
        )
        for row in rows
    ]
