"""
The definition of the command line interface, using `click`.

Not actual work is defined here, but merely how to interact from the console.
All work is delegated to `Controller`.
"""

import sys

import click

from ..controller.controller import Controller


def create_cli():
    controller = Controller(skip_combined_info=True)

    # noinspection PyShadowingNames
    @click.group(invoke_without_command=True, chain=True)
    @click.pass_context
    def aox(ctx):
        # If we're about to run `init-settings`, don't load the combined info,
        # to avoid any "missing settings" messages.
        if not (ctx.invoked_subcommand and sys.argv[1:2] == 'init-settings'):
            controller.reload_combined_info()
        if ctx.invoked_subcommand:
            return
        controller.list_years_and_days(None)

    @aox.command()
    def init_settings():
        controller.init_settings()

    @aox.command()
    def dump_data():
        controller.dump_data()

    @aox.command(context_settings={'ignore_unknown_options': True})
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    @click.option('-f', '--force', 'force', is_flag=True)
    @click.argument('rest', nargs=-1, type=click.UNPROCESSED)
    def challenge(year: int, day: int, part: str, force: bool, rest):
        controller.challenge(year, day, part, force, rest)

    @aox.command()
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    @click.argument('part', type=click.Choice(['a', 'b']))
    def add(year: int, day: int, part: str):
        controller.add_challenge(year, day, part)

    @aox.command()
    @click.argument('year', type=int)
    @click.argument('day', type=int)
    def refresh_challenge_input(year, day):
        controller.refresh_challenge_input(year, day)

    @aox.command(name='list')
    @click.option('-y', '--year', type=int)
    def list_years_and_days(year: int):
        controller.list_years_and_days(year)

    @aox.command()
    def fetch():
        controller.fetch_account_info()

    @aox.command()
    def update_readme():
        controller.update_readme()

    return aox


aox = create_cli()
