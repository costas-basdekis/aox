import timeit
from dataclasses import dataclass
from typing import Optional, Callable

__all__ = ['Timer', 'DummyTimer']


class DummyTimer:
    """
    A dummy timer, useful for testing. It increments in each call by a specified
    amount, not as time passes.
    """
    def __init__(self, start: float = 0, increment:float = 1):
        self.next_value = start
        self.increment = increment

    def __repr__(self) -> str:
        return f"DT({self.next_value}, {self.increment})"

    def __call__(self) -> float:
        """
        >>> DummyTimer()()
        0
        >>> timer = DummyTimer()
        >>> [timer(), timer(), timer()]
        [0, 1, 2]
        >>> timer = DummyTimer(start=2, increment=3)
        >>> [timer(), timer(), timer()]
        [2, 5, 8]
        """
        value = self.next_value
        self.next_value += self.increment
        return value


@dataclass
class Timer:
    """
    A helper class to keep track of time passed since the creation of the
    object.

    It can either be used directly:
        timer = Timer()
        ...
        print(timer.current_duration)
        ...
        timer.finish()
        print(timer.duration)

    Or as a context manager:
        with Timer() as timer:
            ...
            print(timer.current_duration)
            ...
        print(timer.duration)

    You can also either explicity restart the timer:
        timer = Timer()
        ...
        timer.start()

    Or implicitly by using it as a context manager:
        timer = Timer()
        ...
        with timer:
            ...

    >>> Timer(default_timer=DummyTimer())
    Timer(default_timer=DT(1, 1), start=0, end=None)
    >>> timer = Timer(default_timer=DummyTimer())
    >>> [timer.get_current_time(), timer.get_current_time()]
    [1, 2]
    >>> timer.duration
    >>> [timer.current_duration, timer.current_duration]
    [3, 4]
    >>> with timer as timer2:
    ...     timer2 is timer, timer.duration, timer.current_duration
    (True, None, 1)
    >>> timer
    Timer(default_timer=DT(8, 1), start=5, end=7)
    >>> timer.duration, timer.current_duration
    (2, 3)
    >>> with timer as timer2:
    ...     timer2 is timer, timer.duration, timer.current_duration
    (True, None, 1)
    >>> timer
    Timer(default_timer=DT(12, 1), start=9, end=11)
    >>> timer.duration, timer.current_duration
    (2, 3)
    """
    default_timer: Callable[[], float] = timeit.default_timer
    start: float = None
    end: Optional[float] = None

    def __post_init__(self):
        if self.start is None:
            self.start = self.get_current_time()

    def get_current_time(self) -> float:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> [timer.get_current_time(), timer.get_current_time()]
        [1, 2]
        """
        return self.default_timer()

    def begin(self) -> float:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer
        Timer(default_timer=DT(1, 1), start=0, end=None)
        >>> timer.begin()
        1
        >>> timer
        Timer(default_timer=DT(2, 1), start=1, end=None)
        >>> timer.finish()
        2
        >>> timer.begin()
        3
        >>> timer
        Timer(default_timer=DT(4, 1), start=3, end=None)
        """
        self.start = self.get_current_time()
        self.end = None
        return self.start

    def finish(self) -> float:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.finish()
        1
        >>> timer
        Timer(default_timer=DT(2, 1), start=0, end=1)
        """
        self.end = self.get_current_time()
        return self.end

    @property
    def duration(self) -> Optional[float]:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.duration
        >>> timer.finish()
        1
        >>> timer.duration
        1
        >>> timer.begin()
        2
        >>> timer.duration
        >>> timer.finish()
        3
        >>> timer.duration
        1
        """
        if self.end is None:
            return None
        return self.end - self.start

    @property
    def current_duration(self) -> Optional[float]:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.current_duration
        1
        >>> timer.finish()
        2
        >>> timer.duration
        2
        >>> timer.begin()
        3
        >>> timer.current_duration
        1
        >>> timer.finish()
        5
        >>> timer.duration
        2
        """
        return self.get_current_time() - self.start

    def __enter__(self) -> 'Timer':
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.duration, timer.current_duration
        (None, 1)
        >>> with timer as timer2:
        ...     timer2 is timer, timer.duration, timer.current_duration
        (True, None, 1)
        >>> timer.duration, timer.current_duration
        (2, 3)
        """
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()
