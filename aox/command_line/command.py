"""
The definition of the command line interface, using `click`.

Not actual work is defined here, but merely how to interact from the console.
All work is delegated to `Controller`.
"""
from typing import Optional

import click

from ..controller.controller import Controller
from ..settings.settings_class import get_settings, ensure_default_settings

__all__ = ['cli', 'create_cli']


def create_cli():
    """Create a CLI instance to run"""
    controller = Controller()

    @click.group(invoke_without_command=True)
    @click.pass_context
    def aox(ctx):
        # If we're about to run `init-settings`, don't load the combined info,
        # to avoid any "missing settings" messages.
        if ctx.invoked_subcommand != 'init-settings':
            ensure_default_settings()
            controller.reload_combined_info()
        if ctx.invoked_subcommand:
            return
        controller.list_years()

    @aox.command()
    def init_settings():
        controller.init_settings()

    @aox.command()
    def dump_data():
        controller.dump_data()

    @aox.group(invoke_without_command=True)
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    @click.option('-p', '--path', 'path', type=str)
    @click.option('-f', '--force', 'force', is_flag=True)
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.pass_context
    def challenge(ctx, year, day, part, path, force, filters_texts, debug):
        if path is not None:
            year, day, part = get_settings().challenges_boilerplate\
                .extract_from_filename(path)
            ctx.params['year'], ctx.params['day'], ctx.params['part'] = \
                year, day, part
        if ctx.invoked_subcommand:
            return
        controller.test_and_run_challenge(
            year, day, part, force, filters_texts, debug)

    @challenge.command()
    @click.pass_context
    def refresh_input(ctx):
        params = ctx.parent.params
        controller.refresh_challenge_input(
            params['year'], params['day'], only_if_empty=False)

    @challenge.command(name="all")
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.pass_context
    def run_all(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.test_and_run_challenge(
            params['year'], params['day'], params['part'], params['force'],
            params['filters_texts'], params['debug'])

    @challenge.command()
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

    @challenge.command()
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.pass_context
    def run(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.run_challenge(
            params['year'], params['day'], params['part'], params['force'],
            params['debug'])

    @challenge.command()
    @click.pass_context
    def play(ctx):
        params = ctx.parent.params
        controller.play_challenge(
            params['year'], params['day'], params['part'], params['force'])

    @challenge.command()
    @click.option('--yes', '-y', 'no_prompt')
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

    @aox.command()
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    def add(year: int, day: int, part: str):
        controller.add_challenge(year, day, part)

    @aox.command(name='list')
    @click.argument('year', type=int, required=False, default=None)
    def list_years_and_days(year: Optional[int]):
        if year is None:
            controller.list_years()
        else:
            controller.list_days(year)

    @aox.command()
    def fetch():
        controller.fetch_account_info()

    @aox.command()
    def update_readme():
        controller.update_readme()

    return aox


cli = create_cli()
