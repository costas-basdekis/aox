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
from aox.model import RepoInfo, AccountInfo, CombinedInfo, CombinedPartInfo
from aox.settings.settings_class import Settings
from aox.web import WebAoc
from aox.styling.shortcuts import e_warn, e_value, e_success, e_star, e_error, \
    e_unable, e_suggest
from aox.summary import summary_registry
from aox.testing.doctest_enhanced_testmod import testmod_with_filter
from aox.utils import get_current_directory, time_it

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
        settings.validate()
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

    def refresh_challenge_input(self, year, day, only_if_empty=True):
        """Refresh a challenge's input from the AOC website"""
        input_path = settings.challenges_boilerplate\
            .get_day_input_filename(year, day)
        if only_if_empty and input_path.exists() and input_path.lstat().st_size:
            return

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

    def add_challenge(self, year: int, day: int, part: str):
        """Add challenge code boilerplate, if it's not already there"""
        if not settings.challenges_boilerplate.create_part(year, day, part):
            return
        self.refresh_challenge_input(year=year, day=day)
        part_filename = self.combined_info.get_part(year, day, part).path
        click.echo(
            f"Added challenge {e_success(f'{year} {day} {part.upper()}')} at "
            f"{e_value(str(part_filename))}")

        self.update_combined_info(repo_info=RepoInfo.from_roots())

    def challenge(self, year, day, part, force, rest):
        """Invoke a challenge"""
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        challenge_instance.run_main_arguments(args=rest, obj={
            'aox_controller': self,
        })

    def test_and_run_challenge(self, year, day, part, force, filters_texts,
                               debug):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        self.test_challenge(year, day, part, force, filters_texts)
        self.run_challenge(year, day, part, force, debug)

    def test_challenge(self, year, day, part, force, filters_texts):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        filters_text = " ".join(filters_texts)
        test_modules = challenge_instance.get_test_modules()
        with time_it() as stats:
            results = [
                (module,
                 testmod_with_filter(
                     module, optionflags=challenge_instance.optionflags,
                     filters_text=filters_text))
                for module in test_modules
            ]
        total_attempted = sum(result.attempted for _, result in results)
        total_failed = sum(result.failed for _, result in results)
        failed_modules = [
            module.__name__
            if module else
            'main'
            for module, result in results
            if result.failed
        ]
        if failed_modules:
            click.echo(
                f"{e_error(f'{total_failed}/{total_attempted} tests')} "
                f"in {len(failed_modules)}/{len(test_modules)} modules "
                f"{e_error('failed')} "
                f"in {round(stats['duration'], 2)}s"
                f": {e_error(', '.join(failed_modules))}")
        else:
            click.echo(
                f"{total_attempted} tests "
                f"in {len(test_modules)} modules "
                f"{e_success('passed')} "
                f"in {round(stats['duration'], 2)}s")

    def run_challenge(self, year, day, part, force, debug):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        with time_it() as stats:
            solution = challenge_instance.default_solve(debug=debug)
        if solution is None:
            styled_solution = e_error(str(solution))
        else:
            styled_solution = e_value(str(solution))
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {round(stats['duration'], 2)}s)")

    def play_challenge(self, year, day, part, force):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        challenge_instance.play()

    def get_and_submit_challenge_solution(self, year, day, part, force,
                                          no_prompt, solution):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        if not WebAoc().is_configured():
            click.echo(
                f"You haven't set {e_error('AOC_SESSION_ID')} in "
                f"{e_error('user_settings.py')}")
            return None

        solution = self.get_solution(
            challenge_instance, year, day, part, no_prompt, solution)
        if solution is None:
            return

        self.submit_challenge_solution(
            year, day, part, force, no_prompt, solution)

    def submit_challenge_solution(self, year, day, part, force, no_prompt,
                                  solution):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return
        answer_page = WebAoc().submit_solution(year, day, part, solution)
        if not answer_page:
            return

        message = answer_page.article.text
        is_final_part = self.combined_info\
            .get_part(year, day, part).is_final_part
        if "That's the right answer" in message:
            click.echo(
                f"Congratulations! That was {e_success('the right answer')}!\n"
                f"{message}")
            success = True
        elif "Did you already complete it" in message:
            click.echo(
                f"It looks like you have {e_warn('already completed it')}:\n"
                f"{message}")
            success = False
        elif "That's not the right answer" in message:
            click.echo(
                f"It looks like {e_value(solution)} was the "
                f"{e_error('wrong answer')}:\n {message}")
            success = False
        elif "You gave an answer too recently" in message:
            click.echo(
                f"It looks like you need {e_warn('to wait a bit')}:\n{message}")
            success = False
        elif is_final_part and 'congratulations' in message.lower():
            click.echo(
                f"Congratulations! "
                f"{e_success('You completed the whole year!')}!\n"
                f"{message}")
            success = True
        else:
            click.echo(
                f"It's not clear {e_warn('what was the response')}:\n{message}")
            success = False

        if success:
            if no_prompt:
                fetch_and_update_readme = True
            else:
                fetch_and_update_readme = click.prompt(
                    f"Do you want to {e_success('fetch stars')} and "
                    f"{e_success('update the README')}?",
                    type=bool, default=True)
            if fetch_and_update_readme:
                click.echo(
                    f"Fetching {e_star('stars')} and updating "
                    f"{e_success('README')}...")
                self.fetch_account_info()
                self.update_readme()
            else:
                click.echo(
                    f"Make sure to do {e_suggest('aox fetch')} and "
                    f"{e_suggest('aox update-readme')}")

    def get_solution(self, challenge_instance, day, year, part, no_prompt,
                     solution):
        is_final_part = self.combined_info\
            .get_part(year, day, part).is_final_part
        if no_prompt or solution not in (None, ""):
            if is_final_part:
                solve_first = False
                if solution in (None, ""):
                    solution = "1"
            else:
                solve_first = solution in (None, "")
        else:
            if is_final_part:
                default_solution = "1"
            else:
                default_solution = ""
            solution = click.prompt(
                "Run to get the solution, or enter it manually?",
                default=default_solution)
            solve_first = not solution

        if solve_first:
            solution = challenge_instance.default_solve()
        if solution in (None, ""):
            click.echo(f"{e_error('No solution')} was provided")
            return None
        solution = str(solution)

        if not no_prompt:
            old_solution = None
            while old_solution != solution:
                old_solution = solution
                solution = click.prompt(
                    f"Submitting solution {e_value(solution)}",
                    default=solution)
        else:
            click.echo(
                f"Submitting solution {e_value(solution)}")
        if solution in (None, ""):
            click.echo(f"{e_error('No solution')} was provided")
            return None

        return solution

    def get_or_create_challenge(self, year, day, part, force):
        challenge_instance = self.combined_info\
            .get_challenge_instance(year, day, part)
        if not challenge_instance:
            if not self.add_challenge_if_agreed(year, day, part, force):
                return
            challenge_instance = self.combined_info \
                .get_challenge_instance(year, day, part)
        return challenge_instance

    def add_challenge_if_agreed(self, year: int, day: int, part: str,
                                force: bool):
        if not force:
            should_create_challenge = click.prompt(
                f"Do you want to create challenge "
                f"{e_value(f'{year} {day} {part.upper()}')}?",
                type=bool, default=True)
        else:
            should_create_challenge = True
        if not should_create_challenge:
            return False
        self.add_challenge(year=year, day=day, part=part)

        return True

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
