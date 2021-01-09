"""
Provides the interface and an implementation for filtering doctests via a
user-defined filtering expression.

A concrete implementation of `DocTestFilterParser` is used by
`FilteringDocTestFinder`.
"""

import re
from abc import ABC
from doctest import DocTest, Example
from typing import Pattern, Optional, List, Tuple


class InvalidTestFilterException(Exception):
    """
    Raised in `DocTestFilterParser.parse_filters` (and all other methods in it)
    to signify an invalid pattern.
    """


class DocTestFilter(ABC):
    """
    Used by `DocTestFinder` to limit which tests should be run. It's
    usually created by a `DocTestFilterParser`, in response to a user-defined
    filter string.
    """
    def matches_test(self, test: DocTest) -> bool:
        """
        Check if a test should be run based only on the name.
        :param test: The `DocTest` object to check against
        :return: Whether it matches
        """
        raise NotImplementedError()

    def matches_example(self, test: DocTest, example: Example,
                        index: int) -> bool:
        """
        Check if a test's example should be run based on the example's index. It
        is assumed that `matches_test` has already been used to match the `test`
        object.
        :param test: The `DocTest` object which contains `example`
        :param example: The `Example` object to check against
        :param index: The 0-based index of the `Example` within `test`
        :return: Whether it matches
        """
        raise NotImplementedError()


class IndexedDocTestFilter(DocTestFilter):
    """
    Filter in two ways:
    * on the full qualified name of the test (eg 'module.Class.method') via a
    regular expression
    * and also optionally via a list of 0-based text index ranges
    """
    def __init__(self, name_regex: Pattern,
                 number_ranges: Optional[List[range]]):
        """
        :param name_regex: A compiled regular expression from `re.compile`
        :param number_ranges: A list objects that supports the `in` operator.
        Normally this will be a list of `range` objects.
        """
        self.name_regex = name_regex
        self.number_ranges = number_ranges

    def matches_test(self, test: DocTest) -> bool:
        """
        >>> IndexedDocTestFilter(re.compile(r"^method$"), []).matches_test(
        ...     DocTest([], {}, "method", "file.py", 0, ""))
        True
        >>> IndexedDocTestFilter(re.compile(r"^method$"), []).matches_test(
        ...     DocTest([], {}, "another_method", "file.py", 0, ""))
        False
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), []).matches_test(
        ...     DocTest([], {}, "another_method", "file.py", 0, ""))
        True
        """
        return bool(self.name_regex.match(test.name))

    def matches_example(self, test: DocTest, example: Example, index: int
                        ) -> bool:
        """
        >>> a_test = DocTest([], {}, "another_method", "file.py", 0, "")
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), None)\\
        ...     .matches_example(a_test, Example("", ""), 0)
        True
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), [
        ...     range(5),
        ... ]).matches_example(a_test, Example("", ""), 0)
        True
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), [
        ...     range(5),
        ... ]).matches_example(a_test, Example("", ""), 5)
        False
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), [
        ...     range(5), range(10, 20), [5],
        ... ]).matches_example(a_test, Example("", ""), 5)
        True
        >>> IndexedDocTestFilter(re.compile(r"^.*method$"), [
        ...     range(10), range(20), [5],
        ... ]).matches_example(a_test, Example("", ""), 5)
        True
        """
        if self.number_ranges is None:
            return True
        return any(
            index
            in number_range
            for number_range in self.number_ranges
        )


class DocTestFilterParser(ABC):
    """
    Base class for parsing a filtering expression for selecting specific tests
    to run.

    It is based on the premise that the expression is a list of filters that
    can be individually parsed and collated together.
    """

    def parse_filters(self, filters_text: str) -> List[DocTestFilter]:
        """
        Convert a user-provided filter text to a list of filters
        :param filters_text: The user input
        :return: A list of `DocTestFilter` instances
        """
        return [
            self.parse_filter(filter_text)
            for filter_text in self.split_filter_texts(filters_text)
        ]

    re_split_filter_texts = re.compile(r"\s+")

    def split_filter_texts(self, filters_text: str) -> List[str]:
        """
        Split the user input into multiple filters, to be parsed
        :param filters_text: The user input
        :return: A list of strings that each should be converted to a
        `DocTestFilter`
        >>> DocTestFilterParser().split_filter_texts("")
        []
        >>> DocTestFilterParser().split_filter_texts(" " * 20)
        []
        >>> DocTestFilterParser().split_filter_texts("     abc def      ghi   ")
        ['abc', 'def', 'ghi']
        """
        filters_text = filters_text.strip()
        if not filters_text:
            return []
        return self.re_split_filter_texts.split(filters_text)

    def parse_filter(self, filter_text: str) -> DocTestFilter:
        """
        Convert the text for a single filter to a `DocTestFilter`
        :param filter_text: Part of the user input
        :return: `DocTestFilter`
        """
        raise NotImplementedError()


class IndexedDocTestFilterParser(DocTestFilterParser):
    """
    Since we allow the user to pass a filter for selecting tests, this class
    helps with parsing that text, and converting it to a list `DocTestFilter`s.
    It accepts filters with the following attributes:
    * Each filter must have a name suffix specifier
    * Name specifiers can have '*' inside them to match any sub-string
    * The name can not be empty or only '*'
    * Each filter can also optionally contain a set of indexes or ranges of
    indexes to limit which examples are run inside a test
    Examples of understood patterns:
    * method
    * group_of_*_methods
    * specific.module.*.method
    * methods_with_optional_suffix*
    * method:5
    * method:2-5
    * method:2-
    * method:-5
    * method:-3,5-10,15-
    """
    def parse_filter(self, filter_text: str) -> DocTestFilter:
        test_name_text, line_numbers_text = self.get_filter_parts(filter_text)
        return IndexedDocTestFilter(
            self.parse_test_name(test_name_text),
            self.parse_number_ranges(line_numbers_text),
        )

    def get_filter_parts(self, filter_text: str) -> Tuple[str, str]:
        """
        Split the filter into two parts: the name specifier and the index
        specifier.
        :param filter_text: Part of the user input
        :return: A tuple of the name specifier and the index specifier
        >>> IndexedDocTestFilterParser().get_filter_parts("method")
        ('method', '')
        >>> IndexedDocTestFilterParser().get_filter_parts("method:512,3,-7")
        ('method', '512,3,-7')
        >>> IndexedDocTestFilterParser().get_filter_parts(":512,3,-7")
        ('', '512,3,-7')
        >>> IndexedDocTestFilterParser().get_filter_parts(":")
        ('', '')
        >>> IndexedDocTestFilterParser().get_filter_parts(
        ...     "method:512,3,-7:") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        """
        filter_text = filter_text.strip()
        parts = filter_text.split(':')
        if len(parts) > 2:
            raise InvalidTestFilterException(
                f"A filter should have at most two parts, name and ranges, "
                f"not {len(parts)}: '{filter_text}'")

        if len(parts) == 1:
            test_name_text, = parts
            numbers_text = ''
        else:
            test_name_text, numbers_text = parts

        return test_name_text, numbers_text

    def parse_test_name(self, test_name_text: str) -> Pattern:
        """
        Convert a name speficier to a regex:
        * Escape the specifier so that it matches literally the name
        * Convert '*' to regex '.*' to allow to match substrings
        * The resulting regex should not be equivalent to '^.*$', ie it should
        match literally some part of the method
        :param test_name_text: The name specifier, perhaps containing '*'
        :return: The compiled regex
        >>> def test(pattern):
        ...     regex = IndexedDocTestFilterParser().parse_test_name(pattern)
        ...     # noinspection PyUnresolvedReferences
        ...     return [
        ...         name
        ...         for name in [
        ...             f'{part}.{_type}.{prefix}{method}{suffix}'
        ...             for part in ['part_a', 'part_b']
        ...             for _type in ['TypeA', 'TypeB']
        ...             for method in ['method', 'function']
        ...             for suffix in ['', '_plus']
        ...             for prefix in ['', 'plus_']
        ...         ]
        ...         if regex.match(name)
        ...     ]
        >>> test("method") # doctest: +NORMALIZE_WHITESPACE
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_b.TypeA.method', 'part_b.TypeA.plus_method',
            'part_b.TypeB.method', 'part_b.TypeB.plus_method']
        >>> test("method*") # doctest: +NORMALIZE_WHITESPACE
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeA.method_plus', 'part_a.TypeA.plus_method_plus',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_a.TypeB.method_plus', 'part_a.TypeB.plus_method_plus',
            'part_b.TypeA.method', 'part_b.TypeA.plus_method',
            'part_b.TypeA.method_plus', 'part_b.TypeA.plus_method_plus',
            'part_b.TypeB.method', 'part_b.TypeB.plus_method',
            'part_b.TypeB.method_plus', 'part_b.TypeB.plus_method_plus']
        >>> test("part_a.*method") # doctest: +NORMALIZE_WHITESPACE
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method']
        >>> test("part_a.*method*") # doctest: +NORMALIZE_WHITESPACE
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeA.method_plus', 'part_a.TypeA.plus_method_plus',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_a.TypeB.method_plus', 'part_a.TypeB.plus_method_plus']
        >>> test("") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        """
        test_name_text = test_name_text.strip()
        if not test_name_text.replace("*", ""):
            raise InvalidTestFilterException(
                f"You need to specify at least some part of the test name")
        parts = re.split(r'\*+', '*' + test_name_text)
        escaped_parts = map(re.escape, parts)
        return re.compile(f"{'.*'.join(escaped_parts)}$")

    def parse_number_ranges(self, number_ranges_text: str) -> List[range]:
        """
        Convert an index specifier to a list of `range`s, to allow matching
        specific examples. An empty specifier returns one range that should
        match any index.
        Examples:
        * '1': Match a specific example
        * '2-5': Match examples 2 to 5, inclusive
        * '-5': Up to 5, inclusive
        * '2-': From 2 to the end, inclusive
        * '-' or '': Match all examples
        * '-3,5-10,20-': A combination of the above
        :param number_ranges_text: The index specifier for a test
        :return: A list of ranges to match the index of examples
        >>> def test(pattern):
        ...     result = IndexedDocTestFilterParser()\\
        ...         .parse_number_ranges(pattern)
        ...     return sorted(set(sum(map(list, result), [])))[:1010]
        >>> test("") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("-") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("512") # doctest: +ELLIPSIS
        [512]
        >>> test("-512") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 510, 511, 512]
        >>> test("512-") # doctest: +ELLIPSIS
        [512, 513, 514, ..., 1000, 1001, ...]
        >>> test("256-512") # doctest: +ELLIPSIS
        [256, 257, 258, ..., 510, 511, 512]
        >>> test("512-256") # doctest: +ELLIPSIS
        []
        >>> test("256-512-768") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("0xf") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("5-abc") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("1,5,7") # doctest: +ELLIPSIS
        [1, 5, 7]
        >>> test("1,10-20,7") # doctest: +ELLIPSIS
        [1, 7, 10, 11, 12, ..., 18, 19, 20]
        >>> test("1,20-10,7") # doctest: +ELLIPSIS
        [1, 7]
        >>> test("1,20-10,7,10,11") # doctest: +ELLIPSIS
        [1, 7, 10, 11]
        >>> test("1,10-20,-5") # doctest: +ELLIPSIS
        [0, 1, 2, 3, 4, 5, 10, 11, 12, ..., 18, 19, 20]
        >>> test("600-,10-20,-5") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [0, 1, 2, 3, 4, 5, 10, 11, 12, ..., 18, 19, 20, 600, 601, 602,
            ..., 1000, 1001, ...]
        >>> test("600-,10-20,,-5") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("600-,10-20-40,,-5") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("600-,10-0xf,,-5") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("600-,10-abc,,-5") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        """
        return [
            self.parse_number_range(number_range_text)
            for number_range_text in number_ranges_text.split(',')
        ]

    def parse_number_range(self, number_range_text: str) -> range:
        """
        Convert a part of an index specifier to a list of `range`s, to allow
        matching specific examples. An empty specifier returns a range that
        should match any index.
        Examples:
        * '1': Match a specific example
        * '2-5': Match examples 2 to 5, inclusive
        * '-5': Up to 5, inclusive
        * '2-': From 2 to the end, inclusive
        * '-' or '': Match all examples
        :param number_range_text: A part of an index specifier
        :return: A range that matches the respective example indexes
        >>> def test(pattern):
        ...     result = IndexedDocTestFilterParser()\\
        ...         .parse_number_range(pattern)
        ...     return sorted(result)[:1010]
        >>> test("") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("-") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("512") # doctest: +ELLIPSIS
        [512]
        >>> test("-512") # doctest: +ELLIPSIS
        [0, 1, 2, ..., 510, 511, 512]
        >>> test("512-") # doctest: +ELLIPSIS
        [512, 513, 514, ..., 1000, 1001, ...]
        >>> test("256-512") # doctest: +ELLIPSIS
        [256, 257, 258, ..., 510, 511, 512]
        >>> test("512-256") # doctest: +ELLIPSIS
        []
        >>> test("256-512-768") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("0xf") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> test("5-abc") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        """
        number_range_text = number_range_text.strip()
        parts = number_range_text.split('-')
        if len(parts) > 2:
            raise InvalidTestFilterException(
                f"Number ranges must be either a single number "
                f"(eg '512'), or a range either without start (eg '-512'), "
                f"without end (eg '512-') or with just start and end "
                f"(eg '256-512), not with more parts: "
                f"'{number_range_text}'")

        if len(parts) == 1:
            number_text, = parts
            if not number_text:
                start = 0
                end = 10000
            else:
                start = end = self.parse_number(number_text)
        else:
            start_number_text, end_number_text = parts
            if not start_number_text and not end_number_text:
                start = 0
                end = 10000
            elif not start_number_text:
                start = 0
                end = self.parse_number(end_number_text)
            elif not end_number_text:
                start = self.parse_number(start_number_text)
                end = 10000
            else:
                start = self.parse_number(start_number_text)
                end = self.parse_number(end_number_text)

        return range(start, end + 1)

    def parse_number(self, number_text: str) -> int:
        """
        A convenient method to raise an appropriate error if the number to parse
        was not a non-negative integer
        :param number_text: A number string to parse
        :return: The parsed number
        >>> IndexedDocTestFilterParser().parse_number("0")
        0
        >>> IndexedDocTestFilterParser().parse_number("512")
        512
        >>> IndexedDocTestFilterParser().parse_number("-4") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        >>> IndexedDocTestFilterParser()\\
        ...     .parse_number("0xf") # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        doctest.InvalidTestFilterException: ...
        """
        try:
            number = int(number_text)
        except ValueError:
            number = None

        if number is None or number < 0:
            raise InvalidTestFilterException(
                f"Line numbers must be positive integers, not "
                f"'{number_text}'")

        return number
