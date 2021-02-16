"""
All the operations that are provided by the framework can be done via using
`Controller`.
"""

import distutils.dir_util
import json
from dataclasses import dataclass
from doctest import TestResults
from enum import auto
from typing import Optional

import click
from aox.challenge import Debugger

from aox.settings import Settings, settings_proxy
from aox.model import RepoInfo, AccountInfo, CombinedInfo, CombinedPartInfo
from aox.web import WebAoc
from aox.styling.shortcuts import e_warn, e_value, e_success, e_star, e_error, \
    e_unable, e_suggest
from aox.summary import summary_registry
from aox.testing.doctest_enhanced_testmod import testmod_with_filter
from aox.utils import get_current_directory, StringEnum, Timer, \
    has_method_arguments

current_directory = get_current_directory()


@dataclass
class Controller:
    repo_info: Optional[RepoInfo] = None
    account_info: Optional[AccountInfo] = None
    combined_info: Optional[CombinedInfo] = None
    interactive: bool = True

    def init_settings(self, settings_directory=None):
        """Create a new settings directory for the user, if they're missing"""
        if settings_proxy.has() and settings_proxy().path.exists():
            click.echo(
                f"User settings {e_warn('already exist')} at "
                f"{e_value(str(settings_proxy().path))}. Will not overwrite "
                f"them.")
            self.reload_combined_info()
            return False

        self.create_settings(settings_directory=settings_directory)
        self.reload_combined_info()

        return True

    def create_settings(self, settings_directory=None):
        """Create a new settings directory for the user"""
        if settings_directory is None:
            settings_directory = Settings.DEFAULT_SETTINGS_DIRECTORY
        distutils.dir_util.copy_tree(
            Settings.EXAMPLE_SETTINGS_DIRECTORY,
            str(settings_directory))
        settings = Settings.from_settings_directory(settings_directory)
        settings_proxy.set(settings)
        click.echo(
            f"Initialised {e_success('user settings')} at "
            f"{e_value(str(settings_proxy().settings_directory))}! You should "
            f"now edit {e_value(str(settings_proxy().path))} and "
            f"{e_value(str(settings_proxy().sensitive_users_path))}")

    def list_years(self):
        """List all the years that have code or stars"""
        click.echo(
            f"Found {e_success(str(self.combined_info.years_with_code))} years "
            f"with code and "
            f"{e_star(str(self.combined_info.total_stars) + ' stars')}:")
        for year, year_info in sorted(
                self.combined_info.year_infos.items(), reverse=True):
            if not year_info.has_code and not year_info.stars:
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
                not year_info.has_code and not year_info.stars):
            click.echo(
                f"Could not find {e_error(str(year))} in code nor any stars")
            return False
        if not year_info.has_code:
            click.echo(
                f"Could not find {e_error(str(year))} in code, but found "
                f"{e_star(f'{year_info.stars} stars')}")
            return False
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
            for day, day_info
            in sorted(year_info.day_infos.items(), reverse=True)
            if day_info.has_code
        )
        click.echo(f"  * {days_string}")

        return True

    def dump_data(self):
        """Dump the combined data, for diagnostic purposes"""
        if not self.combined_info:
            click.echo(f"There are {e_error('no data loaded')} to dump")
            return False
        print(json.dumps(self.combined_info.serialise(), indent=2))

        return True

    def fetch_account_info(self):
        """Refresh the stars from the AOC website"""
        account_info = AccountInfo.from_site()
        if account_info is None:
            click.echo(f"Could {e_error('not fetch data')}")
            return False

        if settings_proxy().site_data_path:
            with settings_proxy().site_data_path.open('w') as f:
                json.dump(account_info.serialise(), f, indent=2)

        self.update_combined_info(account_info=account_info)
        click.echo(
            f"Fetched data for {e_success(account_info.username)}: "
            f"{e_star(f'{str(account_info.total_stars)} stars')} in "
            f"{e_success(str(len(account_info.year_infos)))} years")

        return True

    def update_readme(self):
        """
        Update README with summaries, presumably because code or stars were
        added.
        """
        readme_path = settings_proxy().readme_path
        if not readme_path:
            return False
        if not self.combined_info.has_site_data:
            click.echo(
                f"Since {e_error('local site data')} are missing the "
                f"README {e_error('cannot be updated')}: run "
                f"{e_suggest('aox fetch')} first")
            return False

        readme_text = readme_path.read_text()

        updated_readme_text = summary_registry.update_text(
            readme_text, self.combined_info)
        if updated_readme_text == readme_text:
            click.echo(f"No need to update {e_success('README')}")
            return False

        readme_path.write_text(updated_readme_text)
        click.echo(f"Updated {e_success('README')} with site data")

        return True

    def refresh_challenge_input(self, year, day, only_if_empty=True):
        """Refresh a challenge's input from the AOC website"""
        input_path = settings_proxy().challenges_boilerplate\
            .get_day_input_filename(year, day)
        if only_if_empty and input_path.exists() and input_path.lstat().st_size:
            return False

        _input = WebAoc().get_input_page(year, day)
        if not _input:
            click.echo(
                f"Could not update input for {e_error(f'{year} {day}')}")
            return False

        if input_path.exists() and _input == input_path.read_text():
            click.echo(
                f"Input did not change for {e_warn(f'{year} {day}')} "
                f"({e_value(f'{len(_input)} bytes')})")
            return False

        input_path.write_text(_input)

        click.echo(
            f"Updated input for {e_success(f'{year} {day}')} "
            f"({e_value(f'{len(_input)} bytes')}) at "
            f"{e_value(str(input_path))}")

        return True

    def add_challenge(self, year: int, day: int, part: str):
        """Add challenge code boilerplate, if it's not already there"""
        if not settings_proxy().challenges_boilerplate\
                .create_part(year, day, part):
            return False
        self.refresh_challenge_input(year=year, day=day)
        part_filename = self.combined_info.get_part(year, day, part).path
        click.echo(
            f"Added challenge {e_success(f'{year} {day} {part.upper()}')} at "
            f"{e_value(str(part_filename))}")
        self.show_challenge_urls(year, day)

        self.update_combined_info(repo_info=RepoInfo.from_roots())

        return True

    def show_challenge_urls(self, year: int, day: int):
        """Show the links to the day and the year"""
        day_info = self.combined_info.get_day(year, day)
        click.echo(
            f"You can see the challenge at {day_info.get_day_url()}, and the "
            f"whole event at {day_info.get_year_url()}")

    def test_and_run_challenge(self, year, day, part, force, filters_texts,
                               debug, debug_interval):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return False, None, None
        test_results = self.test_challenge(
            year, day, part, force, filters_texts)
        _, solution = self.run_challenge(
            year, day, part, force, debug, debug_interval)

        return True, test_results, solution

    def test_challenge(self, year, day, part, force, filters_texts):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return None
        filters_text = " ".join(filters_texts)
        test_modules = challenge_instance.get_test_modules()
        with Timer() as timer:
            modules_and_results = [
                (module,
                 testmod_with_filter(
                     module, optionflags=challenge_instance.optionflags,
                     filters_text=filters_text))
                for module in test_modules
            ]
        results = TestResults(
            attempted=sum(
                result.attempted
                for _, result in modules_and_results
            ),
            failed=sum(
                result.failed
                for _, result in modules_and_results
            ),
        )
        failed_modules = [
            module.__name__
            if module else
            'main'
            for module, result in modules_and_results
            if result.failed
        ]
        if failed_modules:
            click.echo(
                f"{e_error(f'{results.failed}/{results.attempted} tests')} "
                f"in {len(failed_modules)}/{len(test_modules)} modules "
                f"{e_error('failed')} "
                f"in {timer.get_pretty_duration(2)}"
                f": {e_error(', '.join(failed_modules))}")
        else:
            click.echo(
                f"{results.attempted} tests "
                f"in {len(test_modules)} modules "
                f"{e_success('passed')} "
                f"in {timer.get_pretty_duration(2)}")

        return results

    def run_challenge(self, year, day, part, force, debug, debug_interval):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return False, None
        with Timer() as timer:
            debugger = Debugger(
                enabled=debug, min_report_interval_seconds=debug_interval)
            if has_method_arguments(
                    challenge_instance.default_solve, "debugger"):
                solution = challenge_instance.default_solve(debugger=debugger)
            else:
                solution = challenge_instance.default_solve(debug=debugger)
        if solution is None:
            styled_solution = e_error(str(solution))
        else:
            styled_solution = e_value(str(solution))
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {timer.get_pretty_duration(2)})")

        return True, solution

    def play_challenge(self, year, day, part, force):
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return False, None
        result = challenge_instance.play()

        return True, result

    def get_and_submit_challenge_solution(self, year, day, part, force,
                                          no_prompt, solution):
        attempted, submitted, success = False, False, False

        if not WebAoc().is_configured():
            click.echo(
                f"You haven't set {e_error('AOC_SESSION_ID')} in "
                f"{e_error('user_settings.py')}")
            return attempted, submitted, success

        solution = self.get_solution(
            year, day, part, force, no_prompt, solution)
        if solution is None:
            return attempted, submitted, success

        return self.submit_challenge_solution(
            year, day, part, no_prompt, solution)

    def submit_challenge_solution(self, year, day, part, no_prompt, solution):
        attempted, submitted, success = False, False, False

        part_info = self.combined_info\
            .get_part(year, day, part)
        if not part_info:
            return attempted, submitted, success

        attempted = True
        answer_page = WebAoc().submit_solution(year, day, part, solution)
        if not answer_page:
            return attempted, submitted, success

        submitted = True
        message = answer_page.article.text
        is_final_part = part_info.is_final_part
        success, result = self.get_submission_result(is_final_part, message)
        self.echo_submission_result(solution, message, result)

        if success:
            self.fetch_and_update_readme_if_agreed(no_prompt)

        return attempted, submitted, success

    class SubmissionResult(StringEnum):
        RightAnswer = auto()
        AlreadyCompleted = auto()
        WrongAnswer = auto()
        TooSoon = auto()
        RightFinalAnswer = auto()
        Unknown = auto()

    def echo_submission_result(self, solution, message, result):
        """
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.RightAnswer)
        Congratulations! ...
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.AlreadyCompleted)
        It looks like you have already ...
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.WrongAnswer)
        It looks like 1 was the wrong answer...
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.TooSoon)
        It looks like you need to wait ...
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.RightFinalAnswer)
        Congratulations! ...
        >>> Controller().echo_submission_result(
        ...     "1", "Hi", Controller.SubmissionResult.Unknown)
        It's not clear ...
        """
        if result == self.SubmissionResult.RightAnswer:
            click.echo(
                f"Congratulations! That was {e_success('the right answer')}!\n"
                f"{message}"
            )
        elif result == self.SubmissionResult.AlreadyCompleted:
            click.echo(
                f"It looks like you have {e_warn('already completed it')}:\n"
                f"{message}"
            )
        elif result == self.SubmissionResult.WrongAnswer:
            click.echo(
                f"It looks like {e_value(solution)} was the "
                f"{e_error('wrong answer')}:\n {message}"
            )
        elif result == self.SubmissionResult.TooSoon:
            click.echo(
                f"It looks like you need {e_warn('to wait a bit')}:\n{message}"
            )
        elif result == self.SubmissionResult.RightFinalAnswer:
            click.echo(
                f"Congratulations! "
                f"{e_success('You completed the whole year!')}!\n"
                f"{message}"
            )
        elif result == self.SubmissionResult.Unknown:
            click.echo(
                f"It's not clear {e_warn('what was the response')}:\n{message}"
            )
        else:
            raise Exception(f"Don't know how to convey result '{result}'")

    def get_submission_result(self, is_final_part, message):
        """
        >>> import bs4
        >>> from pathlib import Path
        >>> def get_submission_result_from_html(_is_final_part, html_name):
        ...     return Controller().get_submission_result(
        ...        _is_final_part, bs4.BeautifulSoup(Path('').joinpath(
        ...            'tests', 'test_controller', 'test_controller',
        ...            'submission_replies', html_name).read_text(),
        ...            'html.parser').article.text)
        >>> get_submission_result_from_html(False, 'right_answer.html')
        (True, <SubmissionResult.RightAnswer: '...'>)
        >>> get_submission_result_from_html(False, 'already_completed.html')
        (True, <SubmissionResult.AlreadyCompleted: '...'>)
        >>> get_submission_result_from_html(False, 'wrong_answer.html')
        (False, <SubmissionResult.WrongAnswer: '...'>)
        >>> get_submission_result_from_html(False, 'too_soon.html')
        (False, <SubmissionResult.TooSoon: '...'>)
        >>> get_submission_result_from_html(True, 'right_final_answer.html')
        (True, <SubmissionResult.RightFinalAnswer: '...'>)
        >>> get_submission_result_from_html(False, 'unknown.html')
        (False, <SubmissionResult.Unknown: '...'>)
        """
        if "That's the right answer" in message:
            return True, self.SubmissionResult.RightAnswer
        elif "Did you already complete it" in message:
            return True, self.SubmissionResult.AlreadyCompleted
        elif "That's not the right answer" in message:
            return False, self.SubmissionResult.WrongAnswer
        elif "You gave an answer too recently" in message:
            return False, self.SubmissionResult.TooSoon
        elif is_final_part and 'congratulations' in message.lower():
            return True, self.SubmissionResult.RightFinalAnswer
        else:
            return False, self.SubmissionResult.Unknown

    def fetch_and_update_readme_if_agreed(self, no_prompt):
        if no_prompt:
            fetch_and_update_readme = True
        else:
            fetch_and_update_readme = self.prompt(
                f"Do you want to {e_success('fetch stars')} and "
                f"{e_success('update the README')}?",
                type=bool, default=True, no_prompt_default=False)
        if not fetch_and_update_readme:
            click.echo(
                f"Make sure to do {e_suggest('aox fetch')} and "
                f"{e_suggest('aox update-readme')}")
            return

        click.echo(
            f"Fetching {e_star('stars')} and updating "
            f"{e_success('README')}...")
        self.fetch_account_info()
        self.update_readme()

    def get_solution(self, year, day, part, force, no_prompt, solution):
        part_info = self.combined_info\
            .get_part(year, day, part)
        if not part_info:
            return None
        is_final_part = part_info.is_final_part
        if no_prompt or solution not in (None, ""):
            if is_final_part:
                solve_first = False
                if solution in (None, ""):
                    solution = "1"
            else:
                solve_first = solution in (None, "")
        else:
            solve_first = True

        if solve_first:
            challenge_instance = self.get_or_create_challenge(
                year, day, part, force)
            if not challenge_instance:
                return None

            if is_final_part:
                default_solution = "1"
            else:
                default_solution = ""
            if no_prompt:
                solution = default_solution
            else:
                solution = self.prompt(
                    "Run to get the solution, or enter it manually?",
                    default=default_solution,
                    no_prompt_default=default_solution)
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
                solution = self.prompt(
                    f"Submitting solution {e_value(solution)}",
                    default=solution, no_prompt_default=solution)
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
            should_create_challenge = self.prompt(
                f"Do you want to create challenge "
                f"{e_value(f'{year} {day} {part.upper()}')}?",
                type=bool, default=True, no_prompt_default=False)
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

    def prompt(self, text, no_prompt_default, **kwargs):
        if not self.interactive:
            return no_prompt_default
        return click.prompt(text, **kwargs)
