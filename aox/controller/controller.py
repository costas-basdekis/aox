"""
All the operations that are provided by the framework can be done via using
`Controller`.
"""

import distutils.dir_util
import json
import shutil
from dataclasses import dataclass, InitVar
from pathlib import Path
from typing import Optional

import click

from aox.settings import settings
from aox.combined_discovery import CombinedInfo, CombinedPartInfo
from aox.local_discovery import RepoInfo
from aox.settings.settings_class import Settings
from aox.site_discovery import AccountInfo, WebAoc
from aox.styling.shortcuts import e_warn, e_value, e_success, e_star, e_error, \
    e_unable, e_suggest
from aox.summary import summary_registry
from aox.utils import get_current_directory

current_directory = get_current_directory()


@dataclass
class Controller:
    repo_info: Optional[RepoInfo] = None
    account_info: Optional[AccountInfo] = None
    combined_info: Optional[CombinedInfo] = None
    skip_combined_info: InitVar[bool] = False

    def __post_init__(self, skip_combined_info):
        """
        Don't load combined info if requested. This will usually be because
        we're about to initialise settings, so we want to avoid any error
        messages.
        """
        if not skip_combined_info:
            self.reload_combined_info()

    def init_settings(self):
        """Create a new settings directory for the user, if they're missing"""
        if settings.path.exists():
            click.echo(
                f"User settings {e_warn('already exist')} at "
                f"{e_value(str(settings.path))}. Will not overwrite "
                f"them.")
        else:
            self.create_settings()

        self.reload_combined_info()

    def create_settings(self):
        """Create a new settings directory for the user"""
        distutils.dir_util.copy_tree(
            Settings.EXAMPLE_SETTINGS_DIRECTORY,
            str(Settings.DEFAULT_SETTINGS_DIRECTORY))
        click.echo(
            f"Initialised {e_success('user settings')} at "
            f"{e_value(str(Settings.DEFAULT_SETTINGS_DIRECTORY))}! You should "
            f"now edit {e_value(str(Settings.DEFAULT_PATH))} and "
            f"{e_value(str(Settings.DEFAULT_SENSITIVE_USERS_PATH))}")

    def list_years_and_days(self, year: Optional[int]):
        """List years, or days for a year, depending if a year is provided"""
        if year is None:
            self.list_years()
        else:
            self.list_days(year=year)

    def list_years(self):
        """List all the years that have code or stars"""
        click.echo(
            f"Found {e_success(str(len(self.combined_info.year_infos)))} years "
            f"with {e_star(str(self.combined_info.total_stars) + ' stars')}:")
        for year, year_info in sorted(
                self.combined_info.year_infos.items(), reverse=True):
            if not year_info.days_with_code and not year_info.stars:
                continue
            click.echo(
                f"  * {e_success(str(year))}: "
                f"{e_success(str(year_info.days_with_code))} days with code "
                f"and {e_star(f'{year_info.stars} stars')}")

    STATUS_ICON_MAP = {
        CombinedPartInfo.STATUS_COMPLETE: e_star('*'),
        CombinedPartInfo.STATUS_FAILED: e_error('x'),
        CombinedPartInfo.STATUS_DID_NOT_ATTEMPT: '',
        CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT: e_unable('!', fg='white'),
    }

    def list_days(self, year: int):
        """List all the days for a particular year"""
        year_info = self.combined_info.year_infos.get(year)
        if not year_info or (
                not year_info.days_with_code and not year_info.stars):
            click.echo(
                f"Could not find {e_error(str(year))} in code nor any stars")
            return
        if not year_info.days_with_code:
            click.echo(
                f"Could not find {e_error(str(year))} in code, but found "
                f"{e_star(f'{year_info.stars} stars')}")
            return
        click.echo(
            f"Found {e_success(str(year_info.days_with_code))} days with code "
            f"in {e_value(str(year))} with "
            f"{e_star(f'{year_info.stars} stars')}:")
        days_string = ', '.join(
            (
                    e_success(str(day))
                    + self.STATUS_ICON_MAP[day_info.part_infos['a'].status]
                    + self.STATUS_ICON_MAP[day_info.part_infos['b'].status]
            )
            for day, day_info in reversed(year_info.day_infos.items())
            if day_info.parts_with_code
        )
        click.echo(f"  * {days_string}")

    def dump_data(self):
        """Dump the combined data, for diagnostic purposes"""
        if not self.combined_info:
            click.echo(f"There are {e_error('no data loaded')} to dump")
            return
        print(json.dumps(self.combined_info.serialise(), indent=2))

    def fetch_account_info(self):
        """Refresh the stars from the AOC website"""
        account_info = AccountInfo.from_site()
        if account_info is None:
            click.echo(f"Could {e_error('not fetch data')}")
            return

        if settings.site_data_path:
            with settings.site_data_path.open('w') as f:
                json.dump(account_info.serialise(), f, indent=2)

        if not account_info.username:
            star_count_text = 'unknown'
        else:
            star_count_text = str(account_info.total_stars)
            self.update_combined_info(account_info=account_info)
        click.echo(
            f"Fetched data for {e_success(account_info.username)}: "
            f"{e_star(f'{star_count_text} stars')} in "
            f"{e_success(str(len(account_info.year_infos)))} years")

    def update_readme(self):
        """
        Update README with summaries, presumably because code or stars were
        added.
        """
        readme_path = settings.readme_path
        if not readme_path:
            return
        if not self.combined_info.has_site_data:
            click.echo(
                f"Since {e_error('local site data')} are missing the "
                f"README {e_error('cannot be updated')}: run "
                f"{e_suggest('aox fetch')} first")
            return

        readme_text = readme_path.read_text()

        updated_readme_text = summary_registry.update_text(
            readme_text, self.combined_info)
        if updated_readme_text == readme_text:
            click.echo(f"No need to update {e_success('README')}")
            return

        readme_path.write_text(updated_readme_text)
        click.echo(f"Updated {e_success('README')} with site data")

    def refresh_challenge_input(self, year, day):
        """Refresh a challenge's input from the AOC website"""
        challenges_root = settings.challenges_root
        if not challenges_root:
            return
        input_path = challenges_root.joinpath(
            f"year_{year}", f"day_{day:0>2}", "part_a_input.txt")
        _input = WebAoc().get_input_page(year, day)
        if not _input:
            click.echo(
                f"Could not update input for {e_error(f'{year} {day}')}")
            return

        if input_path.exists() and _input == input_path.read_text():
            click.echo(
                f"Input did not change for {e_warn(f'{year} {day}')} "
                f"({e_value(f'{len(_input)} bytes')})")
            return

        input_path.write_text(_input)

        click.echo(
            f"Updated input for {e_success(f'{year} {day}')} "
            f"({e_value(f'{len(_input)} bytes')}) at "
            f"{e_value(str(input_path))}")

    example_year_path = current_directory.joinpath('example_year')
    example_day_path = example_year_path.joinpath('example_day')
    example_part_path = example_day_path.joinpath('example_part.py')

    def add_challenge(self, year: int, day: int, part: str):
        """Add challenge code boilerplate, if it's not already there"""
        challenges_root = settings.challenges_root
        if not challenges_root:
            return
        year_path = challenges_root.joinpath(f"year_{year}")
        day_path = year_path.joinpath(f"day_{day:0>2}")
        part_path = day_path.joinpath(f"part_{part}.py")

        if part_path.exists():
            click.echo(
                f"Challenge {e_warn(f'{year} {day} {part.upper()}')} already "
                f"exists at {e_value(str(part_path))}")
            return

        year_init_path = year_path.joinpath("__init__.py")
        if not year_init_path.exists():
            Path(year_init_path.parent).mkdir(exist_ok=True)
            year_init_path.touch()
        day_init_path = day_path.joinpath("__init__.py")
        if not day_init_path.exists():
            # noinspection PyTypeChecker
            distutils.dir_util.copy_tree(self.example_day_path, str(day_path))
            part_a_path = day_path.joinpath(f"part_{'a'}.py")
            shutil.copy(self.example_part_path, part_a_path)
            self.refresh_challenge_input(year=year, day=day)
        if not part_path.exists():
            shutil.copy(self.example_part_path, part_path)

        click.echo(
            f"Added challenge {e_success(f'{year} {day} {part.upper()}')} at "
            f"{e_value(str(part_path))}")

        self.update_combined_info(repo_info=RepoInfo.from_roots())

    def challenge(self, year: int, day: int, part: str, force: bool, rest):
        """Invoke a challenge"""
        challenge_instance = self.combined_info.get_challenge_instance(
            year, day, part)
        if not challenge_instance:
            if not force:
                should_create_challenge = click.prompt(
                    f"Do you want to create challenge "
                    f"{e_value(f'{year} {day} {part.upper()}')}?",
                    type=bool, default=True)
            else:
                should_create_challenge = True
            if not should_create_challenge:
                return
            self.add_challenge(year=year, day=day, part=part)
            challenge_instance = self.combined_info \
                .get_challenge_instance(year, day, part)
        challenge_instance.run_main_arguments(args=rest, obj={
            'aox_controller': self,
        })

    def reload_combined_info(self):
        """Reload all data from the disk"""
        self.update_combined_info(
            repo_info=RepoInfo.from_roots(),
            account_info=AccountInfo.from_cache(),
        )

    def update_combined_info(self, repo_info=None, account_info=None):
        """
        Update the combined info, presumably after updating either pieces of
        data.
        """
        if repo_info is not None:
            self.repo_info = repo_info
        if account_info is not None:
            self.account_info = account_info
        self.combined_info = CombinedInfo.from_repo_and_account_infos(
            repo_info=self.repo_info,
            account_info=self.account_info,
        )
