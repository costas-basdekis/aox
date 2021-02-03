import io
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import click

from aox.boilerplate import DefaultBoilerplate
from aox.controller.controller import Controller
from aox.model import CombinedInfo, RepoInfo, AccountInfo
from aox.settings import Settings, settings_proxy
from aox.utils.paths import get_root_directory


@contextmanager
def replacing_settings(new_settings):
    old_settings = settings_proxy(False)
    settings_proxy.set(new_settings)
    yield settings_proxy(False)
    settings_proxy.set(old_settings)


@contextmanager
def preparing_to_init_settings():
    with replacing_settings(None), \
         tempfile.TemporaryDirectory() as settings_directory, \
         patch.object(Settings, 'DEFAULT_SETTINGS_DIRECTORY',
                      Path(settings_directory)):
        yield settings_directory


@contextmanager
def amending_settings(**kwargs):
    settings_dict = {
        key: value
        for key, value in settings_proxy().__dict__.items()
        if key in kwargs
    }
    settings_proxy().__dict__.update(**kwargs)
    yield settings_proxy()
    settings_proxy().__dict__.update(settings_dict)


@contextmanager
def resetting_modules(*prefixes):
    try:
        yield
    finally:
        names = [
            name
            for name in sys.modules
            if any(
                name == prefix
                or name.startswith(f"{prefix}.")
                for prefix in prefixes
            )
        ]
        for name in names:
            if name not in sys.modules:
                continue
            try:
                del sys.modules[name]
            except Exception as e:
                print(f"Couldn't remove module {name}: {e}")


@contextmanager
def creating_parts_on_disk(parts):
    with tempfile.TemporaryDirectory(dir=str(get_root_directory())) \
            as challenges_root:
        challenges_module_name_root = Path(challenges_root).name
        extra_settings = {
            "challenges_root": Path(challenges_root),
            "challenges_boilerplate": DefaultBoilerplate(),
            "challenges_module_name_root": challenges_module_name_root,
        }
        with amending_settings(**extra_settings), \
                resetting_modules(challenges_module_name_root):
            for part in parts:
                settings_proxy().challenges_boilerplate.create_part(*part)
            yield challenges_root


@contextmanager
def making_combined_info(parts_to_create_on_disk, collected_data):
    with creating_parts_on_disk(parts_to_create_on_disk):
        yield CombinedInfo \
            .from_repo_and_account_infos(
                RepoInfo.from_roots(),
                AccountInfo.from_collected_data(collected_data),
            )


def make_combined_info(parts_to_create_on_disk, collected_data):
    with making_combined_info(parts_to_create_on_disk, collected_data) \
            as combined_info:
        return combined_info


@contextmanager
def capturing_stdout(color=True):
    original_stdout = sys.stdout
    captured = io.StringIO()
    sys.stdout = captured
    with click.Context(click.Command("dummy"), color=color):
        yield captured
    sys.stdout = original_stdout


@contextmanager
def using_controller(parts_to_create_on_disk, collected_data, color=False,
                     init_settings=False, interactive=True):
    with making_combined_info(parts_to_create_on_disk, collected_data) \
            as combined_info, capturing_stdout(color=color) as captured:
        controller = Controller(interactive=interactive)
        if init_settings:
            controller.init_settings()
        else:
            controller.combined_info = combined_info
        yield controller, combined_info, captured
