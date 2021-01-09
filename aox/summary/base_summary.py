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

    def update_text(self, text, combined_data):
        """Update a text's portion with all the summaries specified"""
        updated = text
        for summary_class in self.summary_classes.values():
            # noinspection PyCallingNonCallable
            updated = summary_class().update_text(updated, combined_data)

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
        """The start marker for a section in a piece of text"""
        return f"[//]: # ({self.marker_prefix}-start)"

    @property
    def end_marker(self):
        """
        The end marker for the a section in a piece of text. It should always
        come after `start_marker`.
        """
        return f"[//]: # ({self.marker_prefix}-end)"

    def generate(self, combined_data):
        """Generate updated section content"""
        raise NotImplementedError()

    def update_text(self, original, combined_data):
        """
        Update text with a new version of content, if the start and end markers
        are present in it.
        """
        summary_indexes = self.get_marker_indexes(original)
        if not summary_indexes:
            return original

        summary_text = self.generate(combined_data)

        return self.replace_text(original, summary_indexes, summary_text)

    def replace_text(self, original, indexes, replacement):
        """Replace a portion of text between the indexes (non-inclusive)"""
        start_index, end_index = indexes

        return "".join([
            original[:start_index],
            replacement,
            original[end_index:],
        ])

    def get_marker_indexes(self, text):
        """Retrieve the start and end marker indexes in a piece of text"""
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

        missing_markers = [
            marker
            for marker, index in [
                (self.start_marker, start_index),
                (self.end_marker, end_index),
            ]
            if index is None
        ]
        if missing_markers:
            missing_markers_text = ', '.join(
                e_error(marker)
                for marker in sorted(missing_markers)
            )
            click.echo(
                f"There were some {e_error('missing markers')} in the README: "
                f"{missing_markers_text} - did you accidentally remove or "
                f"change them?")
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
