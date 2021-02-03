from enum import Enum, auto


__all__ = ['StringEnum']


class StringEnum(Enum):
    """
    An enum class that auto-assigns values to be the same as names

    >>> class TestEnum(StringEnum):
    ...     Foo = auto()
    ...     ClassName = auto()
    ...     ClassNameWithAWSUsingSDK = auto()
    >>> TestEnum.Foo.value
    'foo'
    >>> TestEnum.ClassName.value
    'class-name'
    >>> TestEnum.ClassNameWithAWSUsingSDK.value
    'class-name-with-aws-using-sdk'
    """
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        from aox.utils import tokenize_camel_case
        return tokenize_camel_case(name)
