import re
from typing import Union


__all__ = ['tokenize_camel_case', 'add_thousands_separator']


RES_TOKENIZE_WORDS_BOUNDARY = [
    re.compile(r'([a-z])([A-Z])'),
    re.compile(r'([A-Z])([A-Z][a-z])'),
]


def tokenize_camel_case(name):
    """
    Covert a camel case name to a dash-separated token

    >>> tokenize_camel_case('abc')
    'abc'
    >>> tokenize_camel_case('functionName')
    'function-name'
    >>> tokenize_camel_case('ClassName')
    'class-name'
    >>> tokenize_camel_case('ClassNameWithAWSAbbreviationsSDK')
    'class-name-with-aws-abbreviations-sdk'
    """
    for re_tokenize_words_boundary in RES_TOKENIZE_WORDS_BOUNDARY:
        name = re_tokenize_words_boundary.sub(r'\1-\2', name)
    name = name.lower()

    return name


def add_thousands_separator(number: Union[int, float], separator: str = ",",
                            ) -> str:
    """
    >>> add_thousands_separator(0)
    '0'
    >>> add_thousands_separator(123)
    '123'
    >>> add_thousands_separator(1234)
    '1,234'
    >>> add_thousands_separator(12345)
    '12,345'
    >>> add_thousands_separator(123456)
    '123,456'
    >>> add_thousands_separator(12345678901234567890)
    '12,345,678,901,234,567,890'
    >>> add_thousands_separator(-12345.12345678)
    '-12,345.12345678'
    >>> add_thousands_separator(12345.12345678)
    '12,345.12345678'
    >>> add_thousands_separator(-12345)
    '-12,345'
    >>> add_thousands_separator(-12345.0)
    '-12,345'
    """
    reversed_digits = reversed(str(abs(int(number))))
    from aox.utils import in_groups
    reversed_groups = in_groups(reversed_digits, 3)
    groups = reversed(list(map(reversed, reversed_groups)))
    joined = separator.join(map("".join, groups))
    if number < 0:
        joined = f"-{joined}"
    if float(int(number)) != float(number):
        _, remainder = str(number).split(".")
        joined += f".{remainder}"

    return joined
