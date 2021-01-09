"""
Load the user settings, or if they're missing load the default settings.
"""
import click

from aox.styling.shortcuts import e_error, e_suggest


def load_settings():
    try:
        import user_settings
    except ImportError:
        from . import example_settings
        if not getattr(example_settings, 'has_been_loaded', False):
            click.echo(
                f"Could not load {e_error('user_settings.py')}: using default "
                f"settings - use {e_suggest('aox init-settings')} to create "
                f"your settings file")
        example_settings.is_missing = True
        example_settings.has_been_loaded = True
        return example_settings

    user_settings.is_missing = False
    user_settings.has_been_loaded = True
    return user_settings


settings = load_settings()
