from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional, Dict, Any

import click

from aox.settings import warnings
from aox.styling.shortcuts import e_error, e_suggest
from aox.utils import load_module_from_path, get_current_directory


@warnings.register_warnings
@dataclass
class Settings:
    is_missing: bool
    path: Optional[Path]
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
    site_data_path: Optional[Path] = field(
        default=None,
        metadata={
            "module_attribute": "SITE_DATA_PATH",
            "warn": warnings.warn_missing_path,
        },
    )
    readme_path: Optional[Path] = field(
        default=Path().joinpath('README.md'),
        metadata={
            "module_attribute": "README_PATH",
            "warn": warnings.warn_missing_path,
        },
    )
    _warnings: Dict[str, Any] = field(
        default_factory=warnings.get_warnings_for_new_instance)

    DEFAULT_SETTINGS_DIRECTORY = Path('.aox')
    DEFAULT_PATH = DEFAULT_SETTINGS_DIRECTORY.joinpath('user_settings.py')
    DEFAULT_SENSITIVE_USERS_PATH = DEFAULT_SETTINGS_DIRECTORY\
        .joinpath('sensitive_user_settings.py')
    EXAMPLE_SETTINGS_DIRECTORY = \
        get_current_directory().joinpath('.example-aox')

    @classmethod
    def from_default_path(cls):
        return cls.from_path(cls.DEFAULT_PATH)

    @classmethod
    def from_path(cls, path):
        try:
            settings_module = load_module_from_path(path)
        except (ImportError, FileNotFoundError) as e:
            click.echo(
                f"Could not load {e_error('user_settings.py')} ({e}): using "
                f"default settings - use {e_suggest('aox init-settings')} to "
                f"create your settings file")
            settings_module = None
        return cls.from_settings_module(settings_module, path)

    @classmethod
    def from_settings_module(cls, settings_module, path):
        return cls(
            is_missing=settings_module is None,
            path=path,
            **{
                _field.name: getattr(
                    settings_module,
                    _field.metadata['module_attribute'],
                    _field.default,
                )
                for _field in fields(cls)
                if 'module_attribute' in _field.metadata
            },
        )

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        _warnings = super().__getattribute__('_warnings')
        if item in _warnings:
            warn, module_attribute = _warnings.pop(item)
            value = warn(self, item, module_attribute, value)
            setattr(self, item, value)
        return value


settings = Settings.from_default_path()
