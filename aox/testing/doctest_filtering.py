"""
Implements the filtering functionality that is enabled by the enhanced `testmod`
methods in :mod:`doctest_enhanced_testmod`.
"""

import copy
import doctest
from doctest import DocTest
from typing import List, Optional, Type, Union

from aox.testing.doctest_filter_parsing import IndexedDocTestFilterParser, \
    DocTestFilter, DocTestFilterParser


class FilteringDocTestFinder(doctest.DocTestFinder):
    def __init__(self, verbose=False, parser=doctest.DocTestParser(),
                 recurse=True, exclude_empty=True,
                 parser_class: Type[DocTestFilterParser] =
                 IndexedDocTestFilterParser,
                 filters_text=""):
        super().__init__(verbose=verbose, parser=parser, recurse=recurse,
                         exclude_empty=exclude_empty)
        self.filters: List[DocTestFilter] = \
            parser_class().parse_filters(filters_text)

    def find(self, obj, name=None, module=None, globs=None, extraglobs=None):
        tests = super().find(obj, name, module, globs, extraglobs)

        if self.filters:
            tests = self.filter_tests(tests, self.filters)

        return tests

    def filter_tests(self, tests: List[DocTest],
                     filters_or_text: Union[str, List[DocTestFilter]]) \
            -> List[DocTest]:
        """
        Filter collected tests according a user specification, by using
        `DocTestFilter`s.
        :param tests: The list of tests to filter
        :param filters_or_text: Either a user-specified string, or a parsed one
        :return: A (not necessarily strict) subset of the passed in tests
        """
        if isinstance(filters_or_text, str):
            filters_text = filters_or_text
            filters = DocTestFilterParser().parse_filters(filters_text)
        else:
            filters = filters_or_text

        return list(filter(None, (
            self.filter_test(filters, test)
            for test in tests
        )))

    def filter_test(self, filters, test: DocTest) -> Optional[DocTest]:
        """
        Filter a test according the user specifications. If a test shouldn't be
        run `None` is returned. If it should be, and all of its examples should
        as well, it's returned as is. If only a few of its examples should be,
        a new test with only the appropriate examples is returned.
        :param filters: The user-specified `DocTestFilter`s
        :param test: A test to either discard, accept it fully, or with a subset
        of its examples
        :return: Either `None` to discard the test, the test as is, or a copy
        with fewer examples
        """
        matching_filters = [
            _filter
            for _filter in filters
            if _filter.matches_test(test)
        ]
        if not matching_filters:
            return None
        examples = [
            example
            for index, example in enumerate(test.examples)
            if any(
                _filter.matches_example(test, example, index)
                for _filter in matching_filters
            )
        ]
        if not examples:
            return None

        if examples != test.examples:
            test = copy.copy(test)
            test.examples = examples

        return test
