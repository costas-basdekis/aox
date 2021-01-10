import distutils.dir_util
import importlib
import json
import os
import shutil
import sys
from pathlib import Path

import click

from .. import local_discovery, site_discovery, combined_discovery
from ..settings import settings
from ..settings.loader import EXAMPLE_SETTINGS_DIRECTORY
from ..styling.shortcuts import e_success, e_value, e_warn, e_error, \
    e_suggest, e_star, e_unable
from ..summary import summary_registry

current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
example_year_path = current_directory.joinpath('example_year')
example_day_path = example_year_path.joinpath('example_day')
example_part_path = example_day_path.joinpath('example_part.py')


@click.group(invoke_without_command=True, chain=True)
@click.pass_context
def aox(ctx):
    ctx.obj = {}
    if not (ctx.invoked_subcommand and sys.argv[1:2] == 'init-settings'):
        update_context_object(ctx, {
            'account_info': get_cached_site_data(),
            'repo_info': get_repo_info(),
        })
    if ctx.invoked_subcommand:
        return
    ctx.invoke(list_years_and_days)


def update_context_object(ctx, updates):
    ctx.obj.update(updates)
    ctx.obj['combined_info'] = combined_discovery.CombinedInfo\
        .from_repo_and_account_infos(
            ctx.obj['repo_info'], ctx.obj['account_info'])


def get_cached_site_data():
    if not settings.SITE_DATA_PATH or not settings.SITE_DATA_PATH.exists():
        return None

    with settings.SITE_DATA_PATH.open() as f:
        serialised = json.load(f)

    return site_discovery.AccountInfo.deserialise(serialised)


@aox.command()
@click.pass_context
def init_settings(ctx):
    dot_aox = Path('.aox')
    user_settings_path = dot_aox.joinpath('user_settings.py')
    if user_settings_path.exists():
        click.echo(
            f"User settings {e_warn('already exist')} at "
            f"{e_value(str(user_settings_path))}. Will not overwrite them.")

        update_context_object(ctx, {
            'account_info': get_cached_site_data(),
            'repo_info': get_repo_info(),
        })
        return

    distutils.dir_util.copy_tree(EXAMPLE_SETTINGS_DIRECTORY, str(dot_aox))
    click.echo(
        f"Initialised {e_success('user settings')} at {e_value(str(dot_aox))}! "
        f"You should now edit {e_value(str(user_settings_path))} and "
        f"{e_value(str(dot_aox.joinpath('sensitive_user_settings.py')))}")

    update_context_object(ctx, {
        'account_info': get_cached_site_data(),
        'repo_info': get_repo_info(),
    })


@aox.command()
@click.pass_context
def dump_data(ctx):
    print(json.dumps(ctx.obj["combined_info"].serialise(), indent=2))


@aox.command(context_settings={'ignore_unknown_options': True})
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.option('-f', '--force', 'force', is_flag=True)
@click.argument('rest', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def challenge(ctx, year: int, day: int, part: str, force: bool, rest):
    combined_info = ctx.obj['combined_info']
    challenge_instance = combined_info.get_challenge_instance(year, day, part)
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
        ctx.invoke(add, year=year, day=day, part=part)
        combined_info = ctx.obj['combined_info']
        challenge_instance = combined_info\
            .get_challenge_instance(year, day, part)
    challenge_instance.run_main_arguments(args=rest, obj={
        'aoc_ctx': ctx,
        'aoc_module': importlib.import_module(__name__),
    })


@aox.command()
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.pass_context
def add(ctx, year: int, day: int, part: str):
    challenges_root = get_challenges_root()
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
        distutils.dir_util.copy_tree(example_day_path, str(day_path))
        part_a_path = day_path.joinpath(f"part_{'a'}.py")
        shutil.copy(example_part_path, part_a_path)
        ctx.invoke(refresh_challenge_input, year=year, day=day)
    if not part_path.exists():
        shutil.copy(example_part_path, part_path)

    click.echo(
        f"Added challenge {e_success(f'{year} {day} {part.upper()}')} at "
        f"{e_value(str(part_path))}")

    update_context_object(ctx, {
        'repo_info': get_repo_info(),
    })


def get_challenges_root():
    challenges_root: Path = settings.CHALLENGES_ROOT
    if not challenges_root:
        if settings.is_missing:
            click.echo(
                f"You haven't set {e_error('CHALLENGES_ROOT')} - use "
                f"{e_suggest('aox init-settings')} to create your settings "
                f"file")
        else:
            click.echo(
                f"You haven't set {e_error('CHALLENGES_ROOT')} in "
                f"{e_value('user_settings.py')}")
        return None

    return challenges_root


@aox.command()
@click.argument('year', type=int)
@click.argument('day', type=int)
def refresh_challenge_input(year, day):
    challenges_root = get_challenges_root()
    if not challenges_root:
        return
    input_path = challenges_root.joinpath(
        f"year_{year}", f"day_{day:0>2}", "part_a_input.txt")
    _input = site_discovery.SiteFetcher().get_input_page(year, day)
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
        f"({e_value(f'{len(_input)} bytes')}) at {e_value(str(input_path))}")


@aox.command(name='list')
@click.option('-y', '--year', type=int)
@click.pass_context
def list_years_and_days(ctx, year: int):
    combined_info = ctx.obj['combined_info']
    if year is None:
        list_years(combined_info)
    else:
        list_days(combined_info, year=year)


def list_years(combined_info: combined_discovery.CombinedInfo):
    click.echo(
        f"Found {e_success(str(len(combined_info.year_infos)))} years with "
        f"{e_star(str(combined_info.total_stars) + ' stars')}:")
    for year, year_info in sorted(
            combined_info.year_infos.items(), reverse=True):
        click.echo(
            f"  * {e_success(str(year))}: "
            f"{e_success(str(year_info.days_with_code))} days with code and "
            f"{e_star(f'{year_info.stars} stars')}")


STATUS_ICON_MAP = {
    combined_discovery.CombinedPartInfo.STATUS_COMPLETE: e_star('*'),
    combined_discovery.CombinedPartInfo.STATUS_FAILED: e_error('x'),
    combined_discovery.CombinedPartInfo.STATUS_DID_NOT_ATTEMPT: '',
    combined_discovery.CombinedPartInfo.STATUS_COULD_NOT_ATTEMPT:
    e_unable('!', fg='white'),
}


def list_days(combined_info: combined_discovery.CombinedInfo, year: int):
    if year not in combined_info.year_infos:
        click.echo(f"Could not find {e_error(year)} in code nor any stars")
        return
    year_info: combined_discovery.CombinedYearInfo = \
        combined_info.year_infos[year]
    if not year_info.days_with_code:
        click.echo(
            f"Could not find {e_error(year)} in code, but found "
            f"{e_star(f'{year_info.stars} stars')}")
        return
    click.echo(
        f"Found {e_success(str(year_info.days_with_code))} days with code "
        f"in {e_value(str(year))} with {e_star(f'{year_info.stars} stars')}:")
    days_string = ', '.join(
        (
            e_success(str(day))
            + STATUS_ICON_MAP[day_info.part_infos['a'].status]
            + STATUS_ICON_MAP[day_info.part_infos['b'].status]
        )
        for day, day_info in reversed(year_info.day_infos.items())
        if day_info.parts_with_code
    )
    click.echo(f"  * {days_string}")


def get_repo_info() -> local_discovery.RepoInfo:
    return local_discovery.RepoInfo.from_roots(
        get_challenges_root(), settings.CHALLENGES_MODULE_NAME_ROOT)


@aox.command()
@click.pass_context
def fetch(ctx):
    account_info = get_account_info()
    if account_info is None:
        click.echo(f"Could {e_error('not fetch data')}")
        return

    if settings.SITE_DATA_PATH:
        with settings.SITE_DATA_PATH.open('w') as f:
            json.dump(account_info.serialise(), f, indent=2)

    if not account_info.username:
        star_count_text = 'unknown'
    else:
        star_count_text = str(account_info.total_stars)
        update_context_object(ctx, {
            'account_info': account_info,
        })
    click.echo(
        f"Fetched data for {e_success(account_info.username)}: "
        f"{e_star(f'{star_count_text} stars')} in "
        f"{e_success(str(len(account_info.year_infos)))} years")


def get_account_info() -> site_discovery.AccountInfo:
    return site_discovery.AccountInfo.from_site()


@aox.command()
@click.pass_context
def update_readme(ctx):
    readme_path = get_readme_path()
    if not readme_path:
        return
    combined_info = ctx.obj["combined_info"]
    if not combined_info.has_site_data:
        click.echo(
            f"Since {e_error('local site data')} are missing the "
            f"README {e_error('cannot be updated')}: run "
            f"{e_suggest('aox fetch')} first")
        return

    readme_text = readme_path.read_text()

    updated_readme_text = summary_registry.update_text(
        readme_text, combined_info)
    if updated_readme_text == readme_text:
        click.echo(f"No need to update {e_success('README')}")
        return

    readme_path.write_text(updated_readme_text)
    click.echo(f"Updated {e_success('README')} with site data")


def get_readme_path():
    readme_path: Path = settings.README_PATH
    if not readme_path:
        if settings.is_missing:
            click.echo(
                f"You haven't set {e_error('README_PATH')} - use "
                f"{e_suggest('aox init-settings')} to create your settings "
                f"file")
        else:
            click.echo(
                f"You haven't set {e_error('README_PATH')} in "
                f"{e_value('user_settings.py')}")
        return None

    return readme_path
