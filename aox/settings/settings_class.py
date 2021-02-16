from dataclasses import dataclass, field, fields
from importlib import import_module
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, TYPE_CHECKING

import click

from aox.settings import warnings
from aox.settings.warnings import SettingsValidationError
from aox.styling.shortcuts import e_error, e_suggest
from aox.utils import load_module_from_path, get_current_directory, Module
if TYPE_CHECKING:
    from aox.challenge import Debugger  # noqa: F401

__all__ = [
    'InvalidSettingsError',
    'Settings',
]


class InvalidSettingsError(Exception):
    """
    Error signifying that some validation did not pass during settings
    initialisation.
    """
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


@warnings.register_warnings
@dataclass
class Settings:
    is_missing: bool
    settings_directory: Path
    path: Path
    module: Module
    sensitive_users_path: Path
    aoc_session_id: Optional['str'] = field(
        default=None,
        metadata={
            "module_attribute": "AOC_SESSION_ID",
            "warn": warnings.warn_falsy_attribute,
        },
    )
    challenges_root: Optional[Path] = field(
        default=Path(),
        metadata={
            "module_attribute": "CHALLENGES_ROOT",
            "warn": warnings.warn_missing_path,
        },
    )
    challenges_module_name_root: Optional[str] = field(
        default=None,
        metadata={"module_attribute": "CHALLENGES_MODULE_NAME_ROOT"},
    )
    # noinspection PyUnresolvedReferences
    challenges_boilerplate: 'aox.boilerplate.BaseBoilerplate' = field(  # noqa: F821, E501
        default="aox.boilerplate.DefaultBoilerplate",
        metadata={
            "module_attribute": "CHALLENGES_BOILERPLATE",
            "warn": warnings.error_on(warnings.warn_missing_instance),
            "validate_on_load": True,
        },
    )
    site_data_path: Optional[Path] = field(
        default=None,
        metadata={
            "module_attribute": "SITE_DATA_PATH",
            "warn": warnings.warn_falsy_attribute,
        },
    )
    readme_path: Optional[Path] = field(
        default=Path().joinpath('README.md'),
        metadata={
            "module_attribute": "README_PATH",
            "warn": warnings.warn_missing_path,
        },
    )
    extra_module_imports: List[str] = field(
        default_factory=list,
        metadata={
            "module_attribute": "EXTRA_MODULE_IMPORTS",
        },
    )
    default_debugger_report_format: \
        Optional[Callable[['Debugger', str], str]] = field(
            default=None,
            metadata={
                "module_attribute": "DEFAULT_DEBUGGER_REPORT_FORMAT",
                "warn": warnings.warn_falsy_attribute,
            },
        )
    _warnings: Dict[str, Any] = field(
        default_factory=warnings.get_warnings_for_new_instance)

    DEFAULT_SETTINGS_DIRECTORY = Path('.aox')
    DEFAULT_PATH_NAME = 'user_settings.py'
    DEFAULT_SENSITIVE_USERS_PATH_NAME = 'sensitive_user_settings.py'
    EXAMPLE_SETTINGS_DIRECTORY = \
        get_current_directory().joinpath('.example-aox')

    @classmethod
    def from_default(cls):
        return cls.from_settings_directory(cls.DEFAULT_SETTINGS_DIRECTORY)

    @classmethod
    def from_settings_directory(cls, settings_directory):
        path = settings_directory.joinpath(cls.DEFAULT_PATH_NAME)
        sensitive_users_path = settings_directory\
            .joinpath(cls.DEFAULT_SENSITIVE_USERS_PATH_NAME)
        try:
            settings_module = load_module_from_path(path)
        except (ImportError, FileNotFoundError) as e:
            click.echo(
                f"Could not load {e_error('user_settings.py')} ({e}): using "
                f"default settings - use {e_suggest('aox init-settings')} to "
                f"create your settings file")
            settings_module = None
        return cls.from_settings_module(
            settings_module, settings_directory=settings_directory, path=path,
            sensitive_users_path=sensitive_users_path)

    @classmethod
    def from_settings_module(cls, settings_module, settings_directory, path,
                             sensitive_users_path):
        return cls(
            is_missing=settings_module is None,
            settings_directory=settings_directory,
            path=path,
            module=settings_module,
            sensitive_users_path=sensitive_users_path,
            **{
                _field.name: getattr(
                    settings_module,
                    _field.metadata['module_attribute'],
                )
                for _field in fields(cls)
                if 'module_attribute' in _field.metadata
                and hasattr(
                    settings_module,
                    _field.metadata['module_attribute'],
                )
            },
        )

    def __post_init__(self):
        self.validate()
        self.post_settings_init()

    def validate(self):
        validation_errors = self.get_validation_errors()
        if validation_errors:
            click.echo(
                f"Encountered {e_error('some errors')} while loading settings:"
                f"\n" + "\n".join(
                    f" * {error}"
                    for error in validation_errors
                ))
            raise InvalidSettingsError(
                "Settings were invalid", validation_errors)

    def get_validation_errors(self):
        validation_errors = []
        for _field in fields(self):
            if not _field.metadata.get('validate_on_load', False):
                continue
            try:
                getattr(self, _field.name)
            except SettingsValidationError as e:
                validation_errors.append(e)

        return validation_errors

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        _warnings = super().__getattribute__('_warnings')
        if item in _warnings:
            warn, module_attribute = _warnings.pop(item)
            value = warn(self, item, module_attribute, value)
            setattr(self, item, value)
        return value

    def post_settings_init(self):
        self.load_extra_module_imports()

    def load_extra_module_imports(self):
        for module_name in self.extra_module_imports:
            import_module(module_name)
