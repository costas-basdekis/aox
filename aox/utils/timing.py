import timeit
from contextlib import contextmanager


__all__ = ['time_it']


@contextmanager
def time_it():
    """
    Provide a timer with some useful statistics

    >>> with time_it() as _stats:
    ...     frozen_stats = dict(_stats)
    ...     _stats
    {'start': ..., 'end': None, 'duration': None}
    >>> _stats['start'] == frozen_stats['start']
    True
    >>> frozen_stats
    {'start': ..., 'end': None, 'duration': None}
    >>> _stats['end'] > _stats['start']
    True
    >>> _stats['duration'] == _stats['end'] - _stats['start']
    True
    """
    start = timeit.default_timer()
    stats = {'start': start, 'end': None, 'duration': None}
    yield stats
    end = timeit.default_timer()
    stats.update({'end': end, 'duration': end - start})
