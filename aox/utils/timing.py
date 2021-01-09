import timeit
from contextlib import contextmanager


__all__ = ['time_it']


@contextmanager
def time_it():
    """Provide a timer with some useful statistics"""
    start = timeit.default_timer()
    stats = {'start': start, 'end': None, 'duration': None}
    yield stats
    end = timeit.default_timer()
    stats.update({'end': end, 'duration': end - start})
