from typing import Callable, Tuple

__all__ = ['get_method_arguments', 'has_method_arguments']

from unittest.mock import NonCallableMock


def get_method_arguments(method: Callable) -> Tuple[str, ...]:
    """
    Extract the arguments from a method
    >>> get_method_arguments(lambda: None)
    ()
    >>> get_method_arguments(lambda foo, bar: None)
    ('foo', 'bar')
    >>> get_method_arguments(lambda foo, bar, debug=False: None)
    ('foo', 'bar', 'debug')
    >>> def function(a, b):
    ...     c = a + b
    ...     return c
    >>> get_method_arguments(function)
    ('a', 'b')
    """
    if isinstance(method, NonCallableMock):
        return ()
    # noinspection PyUnresolvedReferences
    method_code = method.__code__
    return method_code.co_varnames[:method_code.co_argcount]


def has_method_arguments(method: Callable, *arguments: str) -> bool:
    """
    Check if a method has the specified arguments

    >>> has_method_arguments(lambda: None)
    True
    >>> has_method_arguments(lambda: None, 'debug')
    False
    >>> has_method_arguments(lambda foo, bar: None, 'debug')
    False
    >>> has_method_arguments(lambda foo, bar, debug=False: None, 'debug')
    True
    >>> has_method_arguments(lambda foo, bar, debug=False: None, 'debug', 'baz')
    False
    >>> has_method_arguments(lambda foo, bar, debug=False: None, 'debug', 'bar')
    True
    >>> def function(a, b):
    ...     c = a + b
    ...     return c
    >>> has_method_arguments(function, 'a')
    True
    >>> has_method_arguments(function, 'debug')
    False
    """
    method_arguments = get_method_arguments(method)
    return all(
        argument in method_arguments
        for argument in arguments
    )
