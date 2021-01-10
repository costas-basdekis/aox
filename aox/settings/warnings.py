from dataclasses import fields

import click

from aox.styling.shortcuts import e_error, e_suggest, e_value


ALL_SETTINGS_WARNINGS = {}


def get_warnings_for_new_instance():
    return dict(ALL_SETTINGS_WARNINGS)


def register_warnings(settings_class):
    for _field in fields(settings_class):
        warn = _field.metadata.get('warn')
        if not warn:
            continue
        module_attribute = _field.metadata["module_attribute"]
        ALL_SETTINGS_WARNINGS[_field.name] = warn, module_attribute

    return settings_class


def warn_falsy_attribute(settings, name, module_attribute, value):
    if value:
        return value
    warn_attribute(settings, name, module_attribute)
    return None


def warn_missing_path(settings, name, module_attribute, value):
    if value and value.exists():
        return value
    warn_attribute(settings, name, module_attribute)
    return None


def warn_attribute(settings, name, module_attribute):
    if settings.is_missing:
        click.echo(
            f"You haven't set {e_error(module_attribute)} - use "
            f"{e_suggest('aox init-settings')} to create your "
            f"settings file")
    else:
        click.echo(
            f"You haven't set {e_error(module_attribute)} in "
            f"{e_value('user_settings.py')}")
