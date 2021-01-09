"""
Load the user settings, or if they're missing load the default settings.
"""
from pathlib import Path

import click

import aox.utils
from aox.styling.shortcuts import e_error, e_suggest


EXAMPLE_SETTINGS_DIRECTORY = aox.utils.get_current_directory()\
    .joinpath('.example-aox')


def load_settings():
    user_settings_path = Path('.aox/user_settings.py')
    try:
        user_settings = aox.utils.load_module_from_path(user_settings_path)
    except (ImportError, FileNotFoundError) as e:
        from . import default_settings
        if not getattr(default_settings, 'has_been_loaded', False):
            click.echo(
                f"Could not load {e_error('user_settings.py')} ({e}): using "
                f"default settings - use {e_suggest('aox init-settings')} to "
                f"create your settings file")
            default_settings.is_missing = True
            default_settings.has_been_loaded = True
        return default_settings

    if not getattr(user_settings, 'has_been_loaded', False):
        user_settings.is_missing = False
        user_settings.has_been_loaded = True
    return user_settings


settings = load_settings()
