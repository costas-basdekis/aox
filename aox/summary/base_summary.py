from dataclasses import dataclass, field
from typing import Dict

import click

from aox.styling.shortcuts import e_error, e_value


__all__ = ['BaseSummary', 'SummaryRegistry', 'summary_registry']


@dataclass
class SummaryRegistry:
    """
    A registry for all the summary classes, so that they can be used to update
    sections in (usually) a README.

    For every new `BaseSummary` subclass, you should use the
    `@summary_registry.register` decorator, or the `summary_registry.override`
    decorator if you want to override one of them.
    """
    summary_classes: Dict[str, 'BaseSummary'] = field(default_factory=dict)
    """
    The summary classes, by their marker prefix identifier.
    """

    def register(self, summary_class: 'BaseSummary', override=False):
        """
        Decorator to register a summary class, that should have a unique
        `marker_prefix` defined, or `override=True` if you want to override an
        already registered summary class.
        """
        marker_prefix = summary_class.marker_prefix
        if marker_prefix is NotImplemented:
            raise Exception(
                f"{summary_class.__name__} didn't set 'marker_prefix'")
        if not override:
            existing_summary_class = self.summary_classes.get(marker_prefix)
            if existing_summary_class:
                raise Exception(
                    f"{summary_class.__name__} tried to override "
                    f"'{marker_prefix}' that was registered by "
                    f"{existing_summary_class.__name__}")
        self.summary_classes[marker_prefix] = summary_class
        return summary_class

    def override(self, summary_class):
        """Handy decorator to override a previous summary class"""
        return self.register(summary_class, override=True)

    def update_text(self, text, combined_info):
        """
        Update a text's portion with all the summaries specified

        >>> test_summary_registry = SummaryRegistry()
        >>> @test_summary_registry.register
        ... class SummaryA(BaseSummary):
        ...     marker_prefix = 'a'
        ...     # noinspection PyShadowingNames
        ...     def generate(self, combined_info):
        ...         return '\\nA\\n'
        >>> @test_summary_registry.register
        ... class SummaryA(BaseSummary):
        ...     marker_prefix = 'b'
        ...     # noinspection PyShadowingNames
        ...     def generate(self, combined_info):
        ...         return '\\nB\\n'
        >>> @test_summary_registry.register
        ... class SummaryE(BaseSummary):
        ...     marker_prefix = 'e'
        ...     # noinspection PyShadowingNames
        ...     def generate(self, combined_info):
        ...         return '\\nE\\n'
        >>> test_summary_registry.update_text(
        ...     '[//]: # (a-start)\\n\\n[//]: # (a-end)\\n'
        ...     '[//]: # (b-start)\\n\\n[//]: # (b-end)\\n'
        ...     '[//]: # (c-start)\\n\\n[//]: # (c-end)\\n'
        ...     '[//]: # (d-start)\\n\\n[//]: # (d-end)\\n'
        ... , None)
        '[//]: # (a-start)\\nA\\n[//]: # (a-end)\\n[//]:
            # (b-start)\\nB\\n[//]: # (b-end)\\n[//]:
            # (c-start)\\n\\n[//]: # (c-end)\\n[//]:
            # (d-start)\\n\\n[//]: # (d-end)\\n'
        >>> test_summary_registry.update_text(
        ...     '[//]: # (a-start)\\n\\n[//]: # (a-end)\\n'
        ...     '[//]: # (b-start)\\n\\n[//]: # (b?-end)\\n'
        ...     '[//]: # (c-start)\\n\\n[//]: # (c-end)\\n'
        ...     '[//]: # (d-start)\\n\\n[//]: # (d-end)\\n'
        ... , None)
        The ... did you accidentally remove or change it?
        '[//]: # (a-start)\\nA\\n[//]: # (a-end)\\n[//]:
            # (b-start)\\n\\n[//]: # (b?-end)\\n[//]:
            # (c-start)\\n\\n[//]: # (c-end)\\n[//]:
            # (d-start)\\n\\n[//]: # (d-end)\\n'
        """
        updated = text
        for summary_class in self.summary_classes.values():
            # noinspection PyCallingNonCallable
            updated = summary_class().update_text(updated, combined_info)

        return updated


class BaseSummary:
    """
    A base class for defining summaries.

    It can generate and update a section in text.

    To be usable automatically, subclasses need to be registered with a
    `@summary_registry.register` or a `@summary_registry.override` decorator.
    """
    marker_prefix: str = NotImplemented
    """
    A unique marker, to be used when delimiting a section in a piece of text,
    and also to uniquely identify it in `summary_registry`.
    """

    @property
    def start_marker(self):
        """
        The start marker for a section in a piece of text

        >>> # noinspection PyAbstractClass
        >>> class TestSummary(BaseSummary):
        ...     marker_prefix = 'summary'
        >>> TestSummary().start_marker
        '[//]: # (summary-start)'
        """
        return f"[//]: # ({self.marker_prefix}-start)"

    @property
    def end_marker(self):
        """
        The end marker for the a section in a piece of text. It should always
        come after `start_marker`.

        >>> # noinspection PyAbstractClass
        >>> class TestSummary(BaseSummary):
        ...     marker_prefix = 'summary'
        >>> TestSummary().end_marker
        '[//]: # (summary-end)'
        """
        return f"[//]: # ({self.marker_prefix}-end)"

    def generate(self, combined_info):
        """Generate updated section content"""
        raise NotImplementedError()

    def update_text(self, text, combined_info):
        """
        Update text with a new version of content, if the start and end markers
        are present in it.

        >>> # noinspection PyAbstractClass
        >>> class TestSummary(BaseSummary):
        ...     marker_prefix = 'summary'
        ...     # noinspection PyShadowingNames
        ...     def generate(self, combined_info):
        ...         return '\\nYo!\\n'
        >>> TestSummary().update_text(
        ...     '[//]: # (dummy-start)\\n'
        ...     '\\n'
        ...     '[//]: # (dummy-end)'
        ... , None)
        '[//]: # (dummy-start)\\n\\n[//]: # (dummy-end)'
        >>> TestSummary().update_text(
        ...     '[//]: # (summary-start)\\n'
        ...     '\\n'
        ...     '[//]: # (dummy-end)'
        ... , None)
        The ... did you accidentally remove or change it?
        '[//]: # (summary-start)\\n\\n[//]: # (dummy-end)'
        >>> TestSummary().update_text(
        ...     '[//]: # (dummy-start)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-end)'
        ... , None)
        The ... did you accidentally remove or change it?
        '[//]: # (dummy-start)\\n\\n[//]: # (summary-end)'
        >>> TestSummary().update_text(
        ...     '[//]: # (summary-end)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-start)'
        ... , None)
        Markers ... not the other way around
        '[//]: # (summary-end)\\n\\n[//]: # (summary-start)'
        >>> TestSummary().update_text(
        ...     '[//]: # (summary-start)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-end)'
        ... , None)
        '[//]: # (summary-start)\\nYo!\\n[//]: # (summary-end)'
        """
        summary_indexes = self.get_marker_indexes(text)
        if not summary_indexes:
            return text

        summary_text = self.generate(combined_info)

        return self.replace_text(text, summary_indexes, summary_text)

    def replace_text(self, text, indexes, replacement):
        """
        Replace a portion of text between the indexes (non-inclusive)

        >>> # noinspection PyAbstractClass
        >>> class TestSummary(BaseSummary):
        ...     marker_prefix = 'summary'
        >>> TestSummary().replace_text(
        ...     '[//]: # (summary-start)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-end)'
        ... , (23, 25), '\\nYo!\\n')
        '[//]: # (summary-start)\\nYo!\\n[//]: # (summary-end)'
        """
        start_index, end_index = indexes

        return "".join([
            text[:start_index],
            replacement,
            text[end_index:],
        ])

    def get_marker_indexes(self, text):
        """
        Retrieve the start and end marker indexes in a piece of text

        >>> # noinspection PyAbstractClass
        >>> class TestSummary(BaseSummary):
        ...     marker_prefix = 'summary'
        >>> TestSummary().get_marker_indexes('')
        >>> TestSummary().get_marker_indexes('[//]: # (summary-start)')
        The ... did you accidentally remove or change it?
        >>> TestSummary().get_marker_indexes('[//]: # (summary-end)')
        The ... did you accidentally remove or change it?
        >>> TestSummary().get_marker_indexes(
        ...     '[//]: # (summary-end)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-start)'
        ... )
        Markers ... not the other way around
        >>> TestSummary().get_marker_indexes(
        ...     '[//]: # (summary-start)\\n'
        ...     '\\n'
        ...     '[//]: # (summary-end)'
        ... )
        (23, 25)
        """
        if self.start_marker in text:
            start_index = (
                text.index(self.start_marker)
                + len(self.start_marker)
            )
        else:
            start_index = None
        if self.end_marker in text:
            end_index = text.index(self.end_marker)
        else:
            end_index = None

        if start_index is None and end_index is None:
            return None
        elif start_index is None:
            click.echo(
                f"The end marker '{self.end_marker}' was present but start "
                f"marker '{e_error(self.start_marker)}' wasn't - did you "
                f"accidentally remove or change it?")
            return None
        elif end_index is None:
            click.echo(
                f"The start marker '{self.start_marker}' was present but end "
                f"marker '{e_error(self.end_marker)}' wasn't - did you "
                f"accidentally remove or change it?")
            return None

        if end_index < start_index:
            click.echo(
                f"Markers for {self.marker_prefix} where in the "
                f"{e_error('opposite order')}: {e_value(self.start_marker)} "
                f"should be before {e_value(self.end_marker)}, not the other "
                f"way around")
            return None

        return start_index, end_index


summary_registry = SummaryRegistry()
