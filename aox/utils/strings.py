import re


__all__ = ['tokenize_camel_case']


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
