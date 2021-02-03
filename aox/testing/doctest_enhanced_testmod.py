"""
Since :mod:`doctest` doesn't allow filtering tests, this provides that
functionality to allow you to select which tests do you want to run.
"""

import doctest
import sys
from typing import Type

from aox.testing.doctest_filter_parsing import DocTestFilterParser, \
    IndexedDocTestFilterParser
from aox.testing.doctest_filtering import FilteringDocTestFinder


def testmod_with_filter(
        m=None, name=None, globs=None, verbose=None, report=True, optionflags=0,
        extraglobs=None, raise_on_error=False, exclude_empty=False,
        parser_class: Type[DocTestFilterParser] = IndexedDocTestFilterParser,
        finder=None, filters_text=""):
    """
    Augment `testmod` with the ability to filter tests via `filters_text`. It
    leverages a version of `testmod` that lets you pass a custom
    `DocTestFinder` instance.

    Optional keyword arg "filters_or_text" specifies either the raw
    user-specified filter text, or the parsed version, in order to limit which
    tests and examples to run. Check the documentation of
    `FilteringDocTestFinder` to see about the syntax.
    """
    if finder is None and filters_text:
        finder = FilteringDocTestFinder(
            exclude_empty=exclude_empty,
            parser_class=parser_class,
            filters_text=filters_text,
        )
    return testmod_with_finder(
        m, name, globs, verbose, report, optionflags, extraglobs,
        raise_on_error, exclude_empty, finder=finder)


def testmod_with_finder(
        m=None, name=None, globs=None, verbose=None, report=True, optionflags=0,
        extraglobs=None, raise_on_error=False, exclude_empty=False,
        finder=None):
    """
    Augment `testmod` with the ability to pass a custom `DocTestFinder`
    instance, that allows for selecting specific tests.

    Optional keyword arg "finder" specifies a finder instance to use, besides
    the default `DocTestFinder`.
    """
    # If no module was given, then use __main__.
    if m is None:
        # DWA - m will still be None if this wasn't invoked from the command
        # line, in which case the following TypeError is about as good an error
        # as we should expect
        m = sys.modules.get('__main__')

    # Check that we were actually given a module.
    import inspect
    if not inspect.ismodule(m):
        raise TypeError("testmod: module required; %r" % (m,))

    # If no name was given, then use the module's name.
    if name is None:
        name = m.__name__

    # Find, parse, and run all tests in the given module.
    if finder is None:
        finder = doctest.DocTestFinder(exclude_empty=exclude_empty)

    if raise_on_error:
        runner = doctest.DebugRunner(verbose=verbose, optionflags=optionflags)
    else:
        runner = doctest.DocTestRunner(verbose=verbose, optionflags=optionflags)

    for test in finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    if report:
        runner.summarize()

    if doctest.master is None:
        doctest.master = runner
    else:
        doctest.master.merge(runner)

    return doctest.TestResults(runner.failures, runner.tries)
