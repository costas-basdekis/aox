from typing import TypeVar, Iterable, Tuple

__all__ = ['in_groups']

T = TypeVar('T')


def in_groups(iterable: Iterable[T], size: int) -> Iterable[Tuple[T, ...]]:
    """
    >>> list(in_groups([], 3))
    []
    >>> list(in_groups(range(5), 3))
    [(0, 1, 2), (3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 3))
    [(0, 1, 2), (3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(6)), 3))
    [(0, 1, 2), (3, 4, 5)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 6))
    [(0, 1, 2, 3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 10))
    [(0, 1, 2, 3, 4)]
    """
    if size < 1:
        raise ValueError(f"Expected size larger than 0, got {size}")
    group = ()
    for item in iterable:
        group += (item,)
        if len(group) >= size:
            yield group
            group = ()
    if group:
        yield group
