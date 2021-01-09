"""
Load the user settings, or if they're missing load the default settings.
"""
import click

from aox.styling.shortcuts import e_error, e_suggest


def load_settings():
    try:
        import user_settings
    except ImportError:
        from . import default_settings
        if not getattr(default_settings, 'has_been_loaded', False):
            click.echo(
                f"Could not load {e_error('user_settings.py')}: using default "
                f"settings - use {e_suggest('aox init-settings')} to create "
                f"your settings file")
            default_settings.is_missing = True
            default_settings.has_been_loaded = True
        return default_settings

    if not getattr(user_settings, 'has_been_loaded', False):
        user_settings.is_missing = False
        user_settings.has_been_loaded = True
    return user_settings


settings = load_settings()
