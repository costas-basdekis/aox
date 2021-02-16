import timeit
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Callable, Union

__all__ = ['Timer', 'DummyTimer', 'pretty_duration']


class DummyTimer:
    """
    A dummy timer, useful for testing. It increments in each call by a specified
    amount, not as time passes.
    """
    def __init__(self, start: float = 0, increment: float = 1):
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
    def pretty_duration(self) -> Optional[str]:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.pretty_duration
        >>> timer.finish()
        1
        >>> timer.pretty_duration
        '1s'
        >>> timer.begin()
        2
        >>> timer.pretty_duration
        >>> timer.finish()
        3
        >>> timer.pretty_duration
        '1s'
        """
        return self.get_pretty_duration()

    def get_pretty_duration(self, digits: Optional[int] = None
                            ) -> Optional[str]:
        duration = self.duration
        if duration is None:
            return None
        return pretty_duration(duration, digits=digits)

    @property
    def current_duration(self) -> float:
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

    @property
    def pretty_current_duration(self) -> str:
        """
        >>> timer = Timer(default_timer=DummyTimer())
        >>> timer.pretty_current_duration
        '1s'
        >>> timer.finish()
        2
        >>> timer.duration
        2
        >>> timer.begin()
        3
        >>> timer.pretty_current_duration
        '1s'
        >>> timer.finish()
        5
        >>> timer.duration
        2
        """
        return self.get_pretty_current_duration()

    def get_pretty_current_duration(self, digits: Optional[int] = None) -> str:
        return pretty_duration(self.current_duration, digits=digits)

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


PRETTY_TIME_LEVELS = [
    # Suffix, factor, next_factor, rounding
    ('s', 60, False),
    ('m', 60, True),
    ('h', 24, True),
    ('d', 7, True),
    ('w', 52, True),
    ('y', None, True),
]


def pretty_duration(duration: float, digits: Optional[int] = None) -> str:
    """
    >>> list(map(pretty_duration, [0, 1, 2.345, 59.234]))
    ['0s', '1s', '2.345s', '59.234s']
    >>> list(map(pretty_duration, [60, 61, 62.345, 3599.234]))
    ['1m0s', '1m1s', '1m2.345s', '59m59.234s']
    >>> list(map(pretty_duration, [3600, 3601, 3662.345, 86399.234]))
    ['1h0m0s', '1h0m1s', '1h1m2.345s', '23h59m59.234s']
    >>> pretty_duration(1 + 60 * (2 + 60 * (3 + 24 * (4 + 7 * (5 + 52 * 6)))))
    '6y5w4d3h2m1s'
    >>> pretty_duration(1 + 60 * (2 + 60 * (3 + 24 * (4 + 7 * (5 + 52 * 999)))))
    '999y5w4d3h2m1s'
    >>> # noinspection PyUnresolvedReferences
    >>> [pretty_duration(x, 1) for x in [59, 59.234, 3599.234, 86399.234]]
    ['59s', '59.2s', '59m59.2s', '23h59m59.2s']
    """
    if duration is None:
        raise ValueError("pretty_duration cannot display a None value")
    if not duration:
        return "0s"
    is_negative = duration < 0
    if is_negative:
        duration *= -1
    remaining = duration
    if digits is not None:
        remaining = round(remaining, digits)
    pretty = ""
    for suffix, next_factor, rounding in PRETTY_TIME_LEVELS:
        if next_factor is not None:
            value = preserve_precision_modulo(remaining, next_factor)
        else:
            value = remaining
        remaining -= value
        if next_factor is not None:
            remaining /= next_factor
        if rounding:
            value = int(value)
        value = remove_unnecessary_precision(value)
        pretty = f"{value}{suffix}{pretty}"
        if not remaining:
            break

    if is_negative:
        pretty = f"-{pretty}"

    return pretty


def preserve_precision_modulo(number: float, divisor: int) -> float:
    """
    >>> preserve_precision_modulo(3599, 60)
    59.0
    >>> preserve_precision_modulo(3599.2, 60)
    59.2
    """
    return float(Decimal(str(number)) % divisor)


def remove_unnecessary_precision(number: float) -> Union[int, float]:
    """
    >>> remove_unnecessary_precision(59)
    59
    >>> remove_unnecessary_precision(59.0)
    59
    >>> remove_unnecessary_precision(59.1)
    59.1
    >>> remove_unnecessary_precision(59.10)
    59.1
    """
    if number == int(number):
        number = int(number)

    return number
