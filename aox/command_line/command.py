"""
The definition of the command line interface, using `click`.

Not actual work is defined here, but merely how to interact from the console.
All work is delegated to `Controller`.
"""
from typing import Optional

import click

from ..controller.controller import Controller
from aox.settings import settings_proxy

__all__ = ['cli', 'create_cli']

from aox.version import AOX_VERSION_LABEL


def create_cli():
    """Create a CLI instance to run"""
    controller = Controller()

    @click.group(
        invoke_without_command=True,
        help=(
            "A utility tool to manage your code, and display a summary of your "
            "stars, for your Advent of Code submissions\n"
            "\n"
            f"Version: {AOX_VERSION_LABEL}"
        ),
        short_help="Manage code & stars for AOC submissions",
    )
    @click.option('-v', '--version', 'show_version', is_flag=True)
    @click.pass_context
    def aox(ctx, show_version=False):
        if show_version:
            ctx.invoke(version)
            return
        # If we're about to run `init-settings`, don't load the combined info,
        # to avoid any "missing settings" messages.
        if ctx.invoked_subcommand != 'init-settings':
            settings_proxy.ensure_default()
            controller.reload_combined_info()
        if ctx.invoked_subcommand:
            return
        controller.list_years()

    @aox.command(
        help=(
            f"Show current version: {AOX_VERSION_LABEL}"
        ),
        short_help=f"Current version: {AOX_VERSION_LABEL}",
    )
    def version():
        click.echo(AOX_VERSION_LABEL)

    @aox.command(
        help=(
            "Initialise settings for the `aox` utility. Necessary to customise "
            "the behaviour, and to cache stars data"
        ),
        short_help="Initialise local settings",
    )
    def init_settings():
        controller.init_settings()

    @aox.command(
        help=(
            "Dump all the internal data that `aox` knows about, usually for "
            "debugging purposes. The output is JSON, and normally quite big "
            "and verbose."
        ),
        short_help="Dump internal data",
    )
    def dump_data():
        controller.dump_data()

    @aox.group(
        invoke_without_command=True,
        help=(
            "Create, test & run a particular challenge, or do other operations "
            "on it"
        ),
        short_help="Create and Test & run a challenge",
    )
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    @click.option('-p', '--path', 'path', type=str)
    @click.option('-f', '--force', 'force', is_flag=True)
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def challenge(ctx, year, day, part, path, force, filters_texts, debug,
                  debug_interval):
        if path is not None:
            year, day, part = settings_proxy().challenges_boilerplate\
                .extract_from_filename(path)
            ctx.params['year'], ctx.params['day'], ctx.params['part'] = \
                year, day, part
        if ctx.invoked_subcommand:
            return
        controller.test_and_run_challenge(
            year, day, part, force, filters_texts, debug, debug_interval)

    @challenge.command(
        help=(
            "Fetch or refresh your personalised input for this challenge from "
            "the AOC website"
        ),
        short_help="Fetch the challenge input",
    )
    @click.pass_context
    def refresh_input(ctx):
        params = ctx.parent.params
        controller.refresh_challenge_input(
            params['year'], params['day'], only_if_empty=False)

    @challenge.command(
        name="url",
        help=(
            "Show the URLs to the day and year for this challenge"
        ),
        short_help="Show day and year URLs",
    )
    @click.pass_context
    def show_urls(ctx):
        params = ctx.parent.params
        controller.show_challenge_urls(params['year'], params['day'])

    @challenge.command(
        name="all",
        help=(
            "Test and run the challenge code"
        ),
        short_help="Test and run challenge",
    )
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def run_all(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.test_and_run_challenge(
            params['year'], params['day'], params['part'], params['force'],
            params['filters_texts'], params['debug'], params['debug_interval'])

    @challenge.command(
        help=(
            "Test the challenge, based on doctests in the file"
        ),
        short_help="Run tests",
    )
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.pass_context
    def test(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.test_challenge(
            params['year'], params['day'], params['part'], params['force'],
            params['filters_texts'])

    @challenge.command(
        help=(
            "Run the challenge and print the solution"
        ),
        short_help="Run the challenge",
    )
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def run(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.run_challenge(
            params['year'], params['day'], params['part'], params['force'],
            params['debug'], params['debug_interval'])

    @challenge.command(
        help=(
            "If the challenge offers an interactive play mode, run it. The "
            "challenge needs to have defined a `Challenge.play` method"
        ),
        short_help="Run interactive mode (if defined)",
    )
    @click.pass_context
    def play(ctx):
        params = ctx.parent.params
        controller.play_challenge(
            params['year'], params['day'], params['part'], params['force'])

    @challenge.command(
        help=(
            "Submit your solution to AOC. You can either provide it (eg if it "
            "takes very long to generate) or run the code and submit the result"
        ),
        short_help="Submit the solution to AOC",
    )
    @click.option('--yes', '-y', 'no_prompt', is_flag=True)
    @click.option('--solution', '-s', 'solution')
    @click.pass_context
    def submit(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.get_and_submit_challenge_solution(
            params['year'], params['day'], params['part'], params['force'],
            params['no_prompt'], params['solution'])

    @aox.command(
        help=(
            "Add the code boilerplate for a challenge"
        ),
        short_help="Add challenge boilerplate",
    )
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    def add(year: int, day: int, part: str):
        controller.add_challenge(year, day, part)

    @aox.command(
        name='list',
        help=(
            "Display a summary of the stars, either for all the years, or a "
            "particular year"
        ),
        short_help="List years/summarise year",
    )
    @click.argument('year', type=int, required=False, default=None)
    def list_years_and_days(year: Optional[int]):
        if year is None:
            controller.list_years()
        else:
            controller.list_days(year)

    @aox.command(
        help=(
            "Fetch all the stars from your AOC account"
        ),
        short_help="Fetch stars data",
    )
    def fetch():
        controller.fetch_account_info()

    @aox.command(
        help=(
            "Update your repo's README with one or more summary formats, "
            "usually displaying stars and links to local code"
        ),
        short_help="Update your README",
    )
    def update_readme():
        controller.update_readme()

    return aox


cli = create_cli()
