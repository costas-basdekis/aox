import doctest
import importlib
import os
import re
import sys
from pathlib import Path

import bs4
import click
import requests

from .. import utils
from ..site_discovery import WebAoc
from ..styling.shortcuts import e_error, e_success, e_value, e_warn, e_star, \
    e_suggest
from ..testing import testmod_with_filter
from ..settings import settings


class BaseChallenge:
    part_a_for_testing = None
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    re_part = re.compile(r"part_([ab])")
    re_day = re.compile(r"day_(\d\d)")
    re_year = re.compile(r"year_(\d\d\d\d)")

    def __init__(self):
        self.module = sys.modules[self.__module__]
        self.input = self.get_input()
        self.part = self.get_part()
        self.day = self.get_day()
        self.year = self.get_year()
        self.is_final_part = (self.day, self.part) == (25, "b")

    def get_part(self):
        path = Path(self.module.__file__)
        part_name = path.name
        part_match = self.re_part.match(part_name)
        if not part_match:
            raise Exception(
                f"Challenge name is not a recognised part 'part_x': "
                f"{part_name}")

        part, = part_match.groups()

        return part

    def get_day(self):
        path = Path(self.module.__file__)
        day_name = path.parent.name
        day_match = self.re_day.match(day_name)
        if not day_match:
            raise Exception(
                f"Challenge path is not a recognised day 'day_xx': "
                f"{day_name}")

        day_text, = day_match.groups()
        day = int(day_text)

        return day

    def get_year(self):
        path = Path(self.module.__file__)
        year_name = path.parent.parent.name
        year_match = self.re_year.match(year_name)
        if not year_match:
            raise Exception(
                f"Challenge path is not a recognised year 'year_xxxx': "
                f"{year_name}")

        year_text, = year_match.groups()
        year = int(year_text)

        return year

    def get_input(self):
        return self.get_current_directory()\
            .joinpath("part_a_input.txt") \
            .read_text()

    def get_current_directory(self):
        return Path(os.path.dirname(os.path.realpath(self.module.__file__)))

    def main(self):
        main_module = sys.modules.get('__main__')
        if self.module != main_module:
            return
        self.run_main_arguments()

    def run_main_arguments(self, args=None, prog_name=None, obj=None):
        cli = self.create_cli()
        cli(args=args, prog_name=prog_name, obj=obj)

    def create_cli(self):
        @click.group(invoke_without_command=True)
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        @click.option('--debug', '-d', 'debug', is_flag=True)
        @click.pass_context
        def cli(*args, **kwargs):
            self.default_command(*args, **kwargs)

        @cli.command(name="all")
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        @click.option('--debug', '-d', 'debug', is_flag=True)
        def run_all(*args, **kwargs):
            self.run_all(*args, **kwargs)

        @cli.command(name="test")
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        def test(*args, **kwargs):
            self.test(*args, **kwargs)

        @cli.command(name="run")
        @click.option('--debug', '-d', 'debug', is_flag=True)
        def run(*args, **kwargs):
            self.run(*args, **kwargs)

        @cli.command(name="play")
        def play():
            self.play()

        @cli.command(name="submit")
        @click.option('--no-prompt', '-y', 'no_prompt', is_flag=True)
        @click.option('--solution', '-s', 'solution')
        @click.pass_context
        def submit(*args, **kwargs):
            self.submit(*args, **kwargs)

        return cli

    def decorate_value(self, decorators, value):
        decorated = value
        for decorator in reversed(decorators):
            decorated = decorator(decorated)

        return decorated

    def default_solve(self, _input=None, debug=False):
        if _input is None:
            _input = self.input
        return self.solve(_input, debug=debug)

    def solve(self, _input, debug=False):
        raise NotImplementedError()

    def default_command(self, ctx, filters_texts=(), debug=False):
        if ctx.invoked_subcommand:
            return
        self.run_all(filters_texts=filters_texts, debug=debug)

    def run_all(self, filters_texts=(), debug=False):
        self.test(filters_texts=filters_texts)
        self.run(debug=debug)

    def play(self):
        raise Exception(f"Challenge has not implemented play")

    def test(self, filters_texts=()):
        filters_text = " ".join(filters_texts)
        test_modules = self.get_test_modules()
        with utils.time_it() as stats:
            results = [
                (module,
                 testmod_with_filter(
                     module, optionflags=self.optionflags,
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
            print(
                f"{e_error(f'{total_failed}/{total_attempted} tests')} "
                f"in {len(failed_modules)}/{len(test_modules)} modules "
                f"{e_error('failed')} "
                f"in {round(stats['duration'], 2)}s"
                f": {e_error(', '.join(failed_modules))}")
        else:
            print(
                f"{total_attempted} tests "
                f"in {len(test_modules)} modules "
                f"{e_success('passed')} "
                f"in {round(stats['duration'], 2)}s")

    def get_test_modules(self):
        modules = [
            importlib.import_module(type(self).__module__),
        ]
        if self.part_a_for_testing:
            modules.append(self.part_a_for_testing)
        return modules

    def run(self, debug=False):
        with utils.time_it() as stats:
            solution = self.default_solve(debug=debug)
        if solution is None:
            styled_solution = e_error(str(solution))
        else:
            styled_solution = e_value(str(solution))
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {round(stats['duration'], 2)}s)")

    def submit(self, ctx, no_prompt=False, solution=None):
        site_fetcher = WebAoc()
        if not site_fetcher.is_configured():
            click.echo(
                f"You haven't set {e_error('AOC_SESSION_ID')} in "
                f"{e_error('user_settings.py')}")
            return None

        if no_prompt:
            if self.is_final_part:
                solve_first = False
                if solution in (None, ""):
                    solution = "1"
            else:
                solve_first = solution in (None, "")
        else:
            if self.is_final_part:
                default_solution = "1"
            else:
                default_solution = ""
            solution = click.prompt(
                "Run to get the solution, or enter it manually?",
                default=default_solution)
            solve_first = not solution

        if solve_first:
            solution = self.default_solve()
        if solution in (None, ""):
            click.echo(f"{e_error('No solution')} was provided")
            return
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
            return

        answer_page = site_fetcher.submit_solution(
            self.year, self.day, self.part, solution)
        if not answer_page:
            return

        message = answer_page.article.text
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
        elif self.is_final_part \
                and 'congratulations' in message.lower():
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
                ctx.obj['aoc_ctx'].invoke(ctx.obj['aoc_module'].fetch)
                ctx.obj['aoc_ctx'].invoke(ctx.obj['aoc_module'].update_readme)
            else:
                click.echo(
                    f"Make sure to do {e_suggest('aox fetch')} and "
                    f"{e_suggest('aox update-readme')}")
