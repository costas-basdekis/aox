from dataclasses import dataclass, field
from typing import Optional, TypeVar

from aox.settings import settings_proxy
from aox.utils import Timer, pretty_duration
from aox.utils import DummyTimer  # noqa: F401

__all__ = ['Debugger']

# noinspection PyTypeChecker
DebuggerT = TypeVar('DebuggerT', bound='Debugger')


@dataclass
class Debugger:
    """
    A debugging helper class, that simplifies outputting debugging information.
    """
    timer: Timer = field(default_factory=Timer)
    """A timer"""
    enabled: bool = True
    """Whether debugging is enabled"""
    step_count: int = 0
    """How many steps have elapsed"""
    step_count_since_last_report: int = 0
    """How many steps have elapsed since the last report?"""
    min_report_interval_seconds: float = 5
    """How much time before two reporting attempts"""
    last_report_time: Optional[float] = None
    """Last time something was reported"""
    indent: str = ""
    """The indent for reporting. Creating a sub-debugger should indent output"""
    indent_increase: str = "  "
    """By how much to increment debugging"""

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.timer.__exit__(exc_tb, exc_val, exc_tb)

    def __bool__(self):
        """
        Convenience method for checking if debugging is enabled

        >>> bool(Debugger())
        True
        >>> bool(Debugger(enabled=False))
        False
        """
        return self.enabled

    def reset(self: DebuggerT) -> DebuggerT:
        """
        Reset counting

        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger
        Debugger(timer=Timer(default_timer=DT(1, 1), start=0, end=None),
            enabled=True, step_count=0, step_count_since_last_report=0,
            min_report_interval_seconds=5, last_report_time=None, indent='',
            indent_increase='  ')
        >>> debugger.report()
        Debugger(timer=Timer(default_timer=DT(2, 1), start=0, end=None),
            enabled=True, step_count=0, step_count_since_last_report=0,
            min_report_interval_seconds=5, last_report_time=1, indent='',
            indent_increase='  ')
        >>> debugger.reset()
        Debugger(timer=Timer(default_timer=DT(3, 1), start=2, end=None),
            enabled=True, step_count=0, step_count_since_last_report=0,
            min_report_interval_seconds=5, last_report_time=None, indent='',
            indent_increase='  ')
        """
        self.timer.__enter__()
        self.step_count = 0
        self.step_count_since_last_report = 0
        self.last_report_time = None

        return self

    def sub_debugger(self: DebuggerT) -> DebuggerT:
        """
        Create a sub-debugger that inherits settings, but starts counting from 0
        time and 0 steps.
        """
        cls = type(self)
        return cls(
            enabled=self.enabled,
            min_report_interval_seconds=self.min_report_interval_seconds,
            indent=self.indent + self.indent_increase,
            indent_increase=self.indent_increase,
        )

    @property
    def duration_since_start(self) -> float:
        """How much time has passed since the start"""
        return self.timer.current_duration

    @property
    def pretty_duration_since_start(self) -> str:
        """A pretty rendition of time passed since the start"""
        return self.get_pretty_duration_since_start()

    def get_pretty_duration_since_start(
            self, digits: Optional[int] = 0) -> str:
        """A pretty rendition of time passed since the start"""
        return self.timer.get_pretty_current_duration(digits)

    @property
    def duration_since_last_report(self) -> Optional[float]:
        """
        How much time has passed since the last reporting attempt
        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger.duration_since_last_report
        >>> debugger.report()
        Debugger(...)
        >>> debugger.duration_since_last_report
        1
        """
        if self.last_report_time is None:
            return None
        return self.timer.get_current_time() - self.last_report_time

    @property
    def pretty_duration_since_last_report(self) -> Optional[str]:
        """A pretty rendition of time passed since the last reporting attempt"""
        return self.get_pretty_duration_since_last_report()

    def get_pretty_duration_since_last_report(
            self, digits: Optional[int] = 0) -> Optional[str]:
        """A pretty rendition of time passed since the last reporting attempt"""
        if self.last_report_time is None:
            return None
        return pretty_duration(self.last_report_time - self.timer.start, digits)

    @property
    def step_frequency(self) -> float:
        """
        How many steps/second have we performed since the beginning?

        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger.step_frequency
        0.0
        >>> debugger.step().step().step()
        Debugger(...)
        >>> debugger.step_frequency
        1.5
        >>> debugger.report().step().step().step()
        Debugger(...)
        >>> debugger.step_frequency
        1.5
        """
        return self.step_count / self.duration_since_start

    @property
    def step_frequency_since_last_report(self) -> float:
        """
        How many steps/second have we performed since the last report (or the
        beginning)?

        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger.step_frequency_since_last_report
        0.0
        >>> debugger.step().step().step()
        Debugger(...)
        >>> debugger.step_frequency_since_last_report
        1.5
        >>> debugger.report().step().step().step()
        Debugger(...)
        >>> debugger.step_frequency_since_last_report
        3.0
        """
        duration = self.duration_since_last_report
        if duration is None:
            duration = self.duration_since_start
        return self.step_count_since_last_report / duration

    def should_report(self) -> bool:
        """
        Is the debugger enable, and has enough time passed since the last
        attempt?

        >>> Debugger().should_report()
        True
        >>> Debugger(enabled=False).should_report()
        False
        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger.should_report()
        True
        >>> debugger.report()
        Debugger(...)
        >>> [debugger.should_report(), debugger.should_report(),
        ...     debugger.should_report(), debugger.should_report()]
        [False, False, False, False]
        >>> [debugger.should_report(), debugger.should_report(),
        ...     debugger.should_report(), debugger.should_report()]
        [True, True, True, True]
        >>> debugger.report()
        Debugger(...)
        >>> [debugger.should_report(), debugger.should_report(),
        ...     debugger.should_report(), debugger.should_report()]
        [False, False, False, False]
        >>> debugger.should_report()
        True
        """
        if not self.enabled:
            return False
        if not self.should_report_after_time():
            return False
        return True

    def should_report_after_time(self) -> bool:
        """Has enough time passed since the last attempt?"""
        duration_since_last_report = self.duration_since_last_report
        if duration_since_last_report is None:
            return True
        return (
            duration_since_last_report
            >= self.min_report_interval_seconds
        )

    def step(self: DebuggerT, step_count: int = 1) -> DebuggerT:
        """Advance the step counter"""
        self.step_count += step_count
        self.step_count_since_last_report += step_count

        return self

    def report(self: DebuggerT, *args, **kwargs) -> DebuggerT:
        """
        Output a message

        >>> Debugger().report()
        Debugger(...)
        >>> Debugger().report("a", "message")
        a message
        Debugger(...)
        >>> Debugger().report("a", "message", sep=",", end="!")
        a,message!Debugger(...)
        >>> Debugger(indent="123").report("a", "message", sep=",", end="!")
        123a,message!Debugger(...)
        >>> Debugger().sub_debugger().report("a", "message")
          a message
        Debugger(...)
        >>> Debugger(indent_increase="??").sub_debugger().report("a", "message")
        ??a message
        Debugger(...)
        """
        if args:
            if self.indent not in (None, ""):
                print(self.indent, end="")
            print(*args, **kwargs)

        self.last_report_time = self.timer.get_current_time()
        self.step_count_since_last_report = 0

        return self

    def default_report(self: DebuggerT, message, **kwargs) -> DebuggerT:
        """
        Output a message with the default format from settings.
        """
        from aox.settings import settings_proxy
        default_debugger_report_format = settings_proxy()\
            .default_debugger_report_format
        if default_debugger_report_format:
            message = default_debugger_report_format(self, message)

        return self.report(message, **kwargs)

    def report_if(self: DebuggerT, *args, **kwargs) -> DebuggerT:
        """
        Output a message, but only if it's appropriate

        >>> debugger = Debugger(timer=Timer(default_timer=DummyTimer()))
        >>> debugger.report_if("a", "message")
        a message
        Debugger(...)
        >>> debugger.report_if("a", "message")
        Debugger(...)
        >>> debugger.report_if("a", "message")
        Debugger(...)
        >>> debugger.report_if("a", "message")
        Debugger(...)
        >>> debugger.report_if("a", "message")
        Debugger(...)
        >>> debugger.report_if("a", "message")
        a message
        Debugger(...)
        """
        if not self.should_report():
            return self
        self.report(*args, **kwargs)

        return self

    def default_report_if(self: DebuggerT, message, **kwargs) -> DebuggerT:
        """
        Output a message with the default format from settings, if it's
        appropriate.
        """
        default_debugger_report_format = settings_proxy()\
            .default_debugger_report_format
        if default_debugger_report_format:
            message = default_debugger_report_format(self, message)

        return self.report_if(message, **kwargs)
