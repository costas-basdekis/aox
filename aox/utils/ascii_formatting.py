__all__ = [
    'join_rows',
    'align_rows',
    'align_divided_rows',
    'simplify_divided_rows',
]


def join_rows(rows, column_separator=' | ', left_pad='| ', right_pad=' |',
              line_separator='\n', align=True):
    """
    Render an ASCII table.

    By default it aligns the columns.

    >>> print(join_rows([])) # doctest: -NORMALIZE_WHITESPACE
    <BLANKLINE>
    >>> print(join_rows([('a', 'b'), ('c', 'd'), ('e', 'f'), ]))
    | a | b |
    | c | d |
    | e | f |
    >>> print(join_rows([
    ...     ('a12', 'b'), ('c', 'd34'), ('e', 'f'),
    ... ])) # doctest: -NORMALIZE_WHITESPACE
    | a12 | b   |
    | c   | d34 |
    | e   | f   |
    >>> print(join_rows([
    ...     ('a12', 'b'), ('c', 'd34'), ('e', 'f'),
    ... ], align=False)) # doctest: -NORMALIZE_WHITESPACE
    | a12 | b |
    | c | d34 |
    | e | f |
    """
    if align:
        rows = align_rows(rows)
    return line_separator.join(
        f"{left_pad}{column_separator.join(row)}{right_pad}"
        for row in rows
    )


def align_rows(rows):
    """
    Visually align rows in the source text of an ASCII table.

    >>> align_rows([]) # doctest: -NORMALIZE_WHITESPACE
    []
    >>> align_rows([
    ...     ('short',), ('short',), ('short',),
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [('short',), ('short',), ('short',)]
    >>> align_rows([
    ...     ('short',), ('a bit longer',), ('very very long',)
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [('short         ',), ('a bit longer  ',), ('very very long',)]
    >>> align_rows([
    ...     ('short', 'short'), ('very very long', 'short'),
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [('short         ', 'short'), ('very very long', 'short')]
    >>> print('\\n'.join(map(' | '.join, align_rows([
    ...     ('short', 'short'), ('very very long', 'short'),
    ... ])))) # doctest: -NORMALIZE_WHITESPACE
    short          | short
    very very long | short
    """
    if not rows:
        return []
    check_rows_have_equal_size(rows)

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


def simplify_divided_rows(divided_rows, part_separator=' ', align=True):
    """
    Join the parts for each column, effectively simplifying it to a
    ready-to-render ASCII table.

    By default it aligns the parts in each column.

    >>> simplify_divided_rows([
    ...     [('short', 'short'), ('a', 'b')],
    ...     [('very very long', 'short'), ('normal', '')],
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [('short          short', 'a      b'), ('very very long short', 'normal  ')]
    >>> simplify_divided_rows([
    ...     [('short', 'short'), ('a', 'b')],
    ...     [('very very long', 'short'), ('normal', '')],
    ... ], align=False) # doctest: -NORMALIZE_WHITESPACE
    [('short short', 'a b'), ('very very long short', 'normal ')]
    """
    if align:
        divided_rows = align_divided_rows(divided_rows)
    return [
        tuple(map(part_separator.join, divided_row))
        for divided_row in divided_rows
    ]


def align_divided_rows(divided_rows):
    """
    Same as `align_rows`, but each column is itself divided in columns that need
    to be aligned. This is useful when you want each column to also have its
    parts aligned.

    >>> align_divided_rows([]) # doctest: -NORMALIZE_WHITESPACE
    []
    >>> align_divided_rows([
    ...     (('1-1-a', '1-1-b'), ('1-2-a', '1-2-b')),
    ...     (('2-1-a', '2-1-b'), ('2-2-a', '2-2-b')),
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [(('1-1-a', '1-1-b'), ('1-2-a', '1-2-b')), \
(('2-1-a', '2-1-b'), ('2-2-a', '2-2-b'))]
    >>> align_divided_rows([
    ...     (('1-1-a-long', '1-1-b'), ('12a', '1-2-b-very-long')),
    ...     (('2-1-a', '2-1-b-long'), ('2-2-a', '2-2-b')),
    ... ]) # doctest: -NORMALIZE_WHITESPACE
    [(('1-1-a-long', '1-1-b     '), ('12a  ', '1-2-b-very-long')), \
(('2-1-a     ', '2-1-b-long'), ('2-2-a', '2-2-b          '))]
    >>> print('\\n'.join(map(
    ...     lambda row: ' | '.join(map(' ~ '.join, row)).rstrip(),
    ...     align_divided_rows([
    ...         (('1-1-a-long', '1-1-b'), ('12a', '1-2-b-very-long')),
    ...         (('2-1-a', '2-1-b-long'), ('2-2-a', '2-2-b')),
    ...     ])))) # doctest: -NORMALIZE_WHITESPACE
    1-1-a-long ~ 1-1-b      | 12a   ~ 1-2-b-very-long
    2-1-a      ~ 2-1-b-long | 2-2-a ~ 2-2-b
    """
    if not divided_rows:
        return []

    check_rows_have_equal_size(divided_rows)

    columns = list(zip(*divided_rows))

    check_columns_have_equal_size(columns)

    aligned_columns = map(align_rows, columns)
    return list(zip(*aligned_columns))


def check_rows_have_equal_size(rows):
    row_sizes = set(map(len, rows))
    if len(row_sizes) != 1:
        raise Exception(
            f"Expected rows of equal size but got multiple sizes: "
            f"{', '.join(map(str, sorted(row_sizes)))}")


def check_columns_have_equal_size(columns):
    uneven_divided_column_sizes = {
        column_index: set(map(len, column))
        for column_index, column in enumerate(columns)
        if len(set(map(len, column))) != 1
    }
    if uneven_divided_column_sizes:
        uneven_columns_message = ', '.join(
            f'{map(str, sorted(column_sizes))} for {column_index}'
            for column_index, column_sizes in uneven_divided_column_sizes
        )
        raise Exception(
            f"Expected columns to be of equal size but got multiple sizes: "
            f"{uneven_columns_message}")
