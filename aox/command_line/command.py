import copy
import distutils.dir_util
import glob
import importlib
import itertools
import json
import os
import re
import shutil
import string
import sys
from pathlib import Path
from typing import List, Tuple

import bs4
import click
import requests

from ..settings import settings
from ..challenge import BaseChallenge
from ..settings.loader import EXAMPLE_SETTINGS_DIRECTORY
from ..styling.shortcuts import e_success, e_value, e_warn, e_error, \
    e_suggest, e_star, e_unable

YearsAndDays = List[Tuple[int, List[int], List[int]]]

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
            'site_data': get_cached_site_data(),
            'years_and_days': get_years_and_days(),
        })
    if ctx.invoked_subcommand:
        return
    ctx.invoke(list_years_and_days)


def update_context_object(ctx, updates):
    ctx.obj.update(updates)
    ctx.obj['combined_data'] = combine_data(
        ctx.obj['site_data'], ctx.obj['years_and_days'])


def get_cached_site_data():
    if not settings.SITE_DATA_PATH or not settings.SITE_DATA_PATH.exists():
        return None

    with settings.SITE_DATA_PATH.open():
        return json.load(settings.SITE_DATA_PATH.open())


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
            'site_data': get_cached_site_data(),
            'years_and_days': get_years_and_days(),
        })
        return

    distutils.dir_util.copy_tree(EXAMPLE_SETTINGS_DIRECTORY, str(dot_aox))
    click.echo(
        f"Initialised {e_success('user settings')} at {e_value(str(dot_aox))}! "
        f"You should now edit {e_value(str(user_settings_path))} and "
        f"{e_value(str(dot_aox.joinpath('sensitive_user_settings.py')))}")

    update_context_object(ctx, {
        'site_data': get_cached_site_data(),
        'years_and_days': get_years_and_days(),
    })


@aox.command()
@click.pass_context
def dump_data(ctx):
    print(json.dumps(ctx.obj["combined_data"], indent=2))


@aox.command(context_settings={'ignore_unknown_options': True})
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.option('-f', '--force', 'force', is_flag=True)
@click.argument('rest', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def challenge(ctx, year: int, day: int, part: str, force: bool, rest):
    combined_data = ctx.obj['combined_data']
    challenge_instance = get_challenge_instance(combined_data, year, day, part)
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
        combined_data = ctx.obj['combined_data']
        challenge_instance = get_challenge_instance(
            combined_data, year, day, part)
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
    day_path = year_path.joinpath("day_{day:0>2}")
    part_path = day_path.joinpath("part_{part}.py")

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
        distutils.dir_util.copy_tree(example_day_path, day_path)
        part_a_path = day_path.joinpath("part_{'a'}.py")
        example_part_path.rename(part_a_path)
        ctx.invoke(refresh_challenge_input, year=year, day=day)
    if not part_path.exists():
        shutil.copy(example_part_path, part_path)

    click.echo(
        f"Added challenge {e_success(f'{year} {day} {part.upper()}')} at "
        f"{e_value(str(part_path))}")

    update_context_object(ctx, {
        'years_and_days': get_years_and_days(),
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
    _input = get_input_from_site(year, day)
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
        f"Updated input for {e_success(f'{year} {day}')} at "
        f"{e_value(str(input_path))} ({e_value(f'{len(_input)} bytes')})")


def get_input_from_site(year, day):
    session_id = get_session_id()
    if not session_id:
        return None

    response = requests.get(
        f'https://adventofcode.com/{year}/day/{day}/input',
        cookies={"session": session_id},
        headers={"User-Agent": "aox"},
    )
    if not response.ok:
        if response.status_code == 404:
            click.echo(
                f"AOC did not know about challenge's "
                f"{e_error(f'{year} {day}')} input: did you enter the wrong "
                f"year/day, is the URL wrong, or are you banned?")
        else:
            click.echo(
                f"Could not get {e_error('the input')} from AOC site - is the "
                f"internet down, AOC down, the URL is wrong, or are you "
                f"banned?")
        return None

    return response.text


def get_session_id():
    session_id = getattr(settings, 'AOC_SESSION_ID')
    if not session_id:
        if settings.is_missing:
            click.echo(
                f"You haven't set {e_error('AOC_SESSION_ID')} - use "
                f"{e_suggest('aox init-settings')} to create your settings "
                f"file")
        else:
            click.echo(
                f"You haven't set {e_error('AOC_SESSION_ID')} in "
                f"{e_value('user_settings.py')}")

    return session_id


def get_challenge_instance(combined_data, year: int, day: int, part: str):
    year_data = combined_data["years"].get(str(year))
    if not year_data:
        click.echo(
            f"It looks like there is no code for {e_error(str(year))}")
        return None
    day_data = year_data["days"].get(str(day))
    if not day_data:
        click.echo(
            f"It looks like there is no code for "
            f"{e_error(f'{year} day {day}')}")
        return None
    part_data = day_data["parts"].get(part)
    if not part_data:
        click.echo(
            f"It looks like there is no code for "
            f"{e_error(f'{year} day {day} part {part}')}")
        return None
    module_name = part_data["module_name"]
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        click.echo(f"Could not find {e_error(module_name)}")
        return None

    if not hasattr(module, 'challenge'):
        challenge_class = getattr(module, 'Challenge')
        if not isinstance(challenge_class, type) \
                or not issubclass(challenge_class, BaseChallenge):
            click.echo(
                f"Challenge {e_error(module_name)} does not use "
                f"`BaseChallenge` and doesn't specify a `challenge` instance")
            return None
        challenge_instance = challenge_class()
    else:
        challenge_instance = getattr(module, 'challenge')

    if not isinstance(challenge_instance, BaseChallenge):
        click.echo(
            f"Challenge {e_error(module_name)} `challenge` instance is not of "
            f"`BaseChallenge`")
        return None

    return challenge_instance


@aox.command(name='list')
@click.option('-y', '--year', type=int)
@click.pass_context
def list_years_and_days(ctx, year: int):
    combined_data = ctx.obj['combined_data']
    if year is None:
        list_years(combined_data)
    else:
        list_days(combined_data, year=str(year))


def list_years(combined_data):
    click.echo(
        f"Found {e_success(str(len(combined_data['years'])))} years with "
        f"{e_star(str(combined_data['total_stars']) + ' stars')}:")
    for year, year_data in sorted(combined_data["years"].items(), reverse=True):
        days_with_code = year_data["days_with_code"]
        year_stars = year_data["stars"]
        click.echo(
            f"  * {e_success(year)}: {e_success(str(days_with_code))} days "
            f"with code and {e_star(f'{year_stars} stars')}")


def list_days(combined_data, year: str):
    if year not in combined_data["years"]:
        click.echo(f"Could not find {e_error(year)} in code nor any stars")
        return
    year_data = combined_data["years"][year]
    year_stars = year_data['stars']
    if not year_data["days_with_code"]:
        click.echo(
            f"Could not find {e_error(year)} in code, but found "
            f"{e_star(f'{year_stars} stars')}")
        return
    click.echo(
        f"Found {e_success(str(year_data['days_with_code']))} days with code "
        f"in {e_value(str(year))} with {e_star(f'{year_stars} stars')}:")
    days_string = ', '.join(
        (
            e_success(str(day), fg='green')
            + get_styled_part_status_icon(day_data["parts"]["a"]["status"])
            + get_styled_part_status_icon(day_data["parts"]["b"]["status"])
        )
        for day, day_data in reversed(year_data["days"].items())
        if day_data["has_code"]
    )
    click.echo(f"  * {days_string}")


def get_styled_part_status_icon(status):
    if status == PART_STATUS_COMPLETE:
        return e_star('*')
    elif status == PART_STATUS_FAILED:
        return e_error('x')
    elif status == PART_STATUS_DID_NOT_ATTEMPT:
        return ''
    elif status == PART_STATUS_COULD_NOT_ATTEMPT:
        return e_unable('!', fg='white')
    else:
        raise Exception(f"Unknown part status '{status}'")


PART_STATUS_COMPLETE = 'complete'
PART_STATUS_FAILED = 'failed'
PART_STATUS_DID_NOT_ATTEMPT = 'did-not-attempt'
PART_STATUS_COULD_NOT_ATTEMPT = 'could-not-attempt'

PART_STATUSES = [
    PART_STATUS_COMPLETE,
    PART_STATUS_FAILED,
    PART_STATUS_DID_NOT_ATTEMPT,
    PART_STATUS_COULD_NOT_ATTEMPT,
]


def combine_data(site_data, years_and_days):
    challenges_root = get_challenges_root()

    if site_data is None:
        combined_data = {
            "has_site_data": False,
            "user_name": None,
            "total_stars": 0,
            "years": {},
        }
    else:
        combined_data = copy.deepcopy(site_data)
        combined_data["has_site_data"] = True
    days_by_year = {
        str(year): days
        for year, days, missing_days in years_and_days
    }
    for year in days_by_year:
        if year not in combined_data['years']:
            combined_data['years'][year] = {
                "stars": 0,
                "days": {
                    str(day): 0
                    for day in range(1, 26)
                },
            }
    for year, year_data in combined_data["years"].items():
        year_stars = year_data["stars"]
        year_data["year"] = year
        if challenges_root:
            year_data["has_code"] = challenges_root\
                .joinpath(f"year_{year}", "__init__.py").exists()
        else:
            year_data["has_code"] = False
        for day, day_stars in list(year_data["days"].items()):
            if challenges_root:
                day_path = challenges_root\
                    .joinpath(f"year_{year}", f"day_{day:0>2}")
                has_part_a = day_path.joinpath(f"part_{'a'}.py").exists()
                has_part_b = day_path.joinpath(f"part_{'b'}.py").exists()
            else:
                has_part_a = False
                has_part_b = False
            if day_stars >= 1:
                part_a_status = PART_STATUS_COMPLETE
            elif has_part_a:
                part_a_status = PART_STATUS_FAILED
            else:
                part_a_status = PART_STATUS_DID_NOT_ATTEMPT
            if day_stars == 2:
                part_b_status = PART_STATUS_COMPLETE
            elif day_stars == 1:
                if day == "25" and year_stars < 49:
                    part_b_status = PART_STATUS_COULD_NOT_ATTEMPT
                elif has_part_b:
                    part_b_status = PART_STATUS_FAILED
                else:
                    part_b_status = PART_STATUS_DID_NOT_ATTEMPT
            elif has_part_a:
                part_b_status = PART_STATUS_COULD_NOT_ATTEMPT
            else:
                part_b_status = PART_STATUS_DID_NOT_ATTEMPT
            year_data["days"][day] = {
                "year": year,
                "day": f"{day:0>2}",
                "stars": day_stars,
                "has_code": has_part_a or has_part_b,
                "parts": {
                    part: {
                        "year": year,
                        "day": f"{day:0>2}",
                        "part": part,
                        "has_code": has_part,
                        "star": day_stars >= minimum_stars,
                        "status": part_status,
                        "module_name": ".".join(filter(None, [
                            settings.CHALLENGES_MODULE_NAME_ROOT,
                            f"year_{year}.day_{day:0>2}.part_{part}",
                        ])),
                    }
                    for part, minimum_stars, has_part, part_status
                    in [
                        ("a", 1, has_part_a, part_a_status),
                        ("b", 2, has_part_b, part_b_status),
                    ]
                }
            }
        year_data["by_part_status"] = {
            **{
                status: 0
                for status in PART_STATUSES
            },
            **{
                part_status: len(list(items))
                for part_status, items in itertools.groupby(sorted(
                    part["status"]
                    for day in year_data["days"].values()
                    for part in day["parts"].values()
                ))
            },
        }
        year_data["days_with_code"] = sum(
            1
            for day_data in year_data["days"].values()
            if day_data["has_code"]
        )
    combined_data["years_with_code"] = sum(
        1
        for year_data in combined_data["years"].values()
        if year_data["days_with_code"] > 0
    )

    return combined_data


def get_years_and_days() -> YearsAndDays:
    challenges_root = get_challenges_root()
    if not challenges_root:
        return []
    part_a_files = glob.glob(
        str(challenges_root.joinpath("year_*", "day_*", "part_a.py")))
    years_and_days = [
        (year, [month for _, month in items])
        for year, items in itertools.groupby(sorted(
            (int(year_text), int(day_text))
            for name in part_a_files
            for year_part, day_part, _ in [name.split('/', 2)]
            for year_text, day_text in [
                (year_part.replace('year_', ''), day_part.replace('day_', '')),
            ]
            if not set(year_text) - set(string.digits)
            and not set(day_text) - set(string.digits)
        ), key=lambda item: item[0])
    ]

    return [
        (year, days, sorted(set(range(1, 26)) - set(days)))
        for year, days in years_and_days
    ]


@aox.command()
@click.pass_context
def fetch(ctx):
    data = update_data_from_site()
    if data is None:
        click.echo(f"Could {e_error('not fetch data')}")
        return

    if settings.SITE_DATA_PATH:
        with settings.SITE_DATA_PATH.open('w') as f:
            json.dump(data, f, indent=2)

    if data['total_stars'] is None:
        star_count_text = 'unknown'
    else:
        star_count_text = str(data['total_stars'])
        update_context_object(ctx, {
            'site_data': data,
        })
    click.echo(
        f"Fetched data for {e_success(data['user_name'])}: "
        f"{e_star(f'{star_count_text} stars')} in "
        f"{e_success(str(len(data['years'])))} years")


def update_data_from_site():
    events_page = get_events_page()

    user_name = get_user_name(events_page)
    if not user_name:
        return None

    total_stars = get_total_stars(events_page)

    years_and_details = get_years_and_details(events_page)

    return {
        "user_name": user_name,
        "total_stars": total_stars,
        "years": years_and_details,
    }


def get_events_page():
    session_id = get_session_id()
    if not session_id:
        return None

    response = requests.get(
        'https://adventofcode.com/events',
        cookies={"session": session_id},
        headers={"User-Agent": "aox"},
    )
    if not response.ok:
        click.echo(
            f"Could not get {e_error('events information')} from "
            f"AOC site - is the internet down, AOC down, the URL is wrong, or "
            f"are you banned?")
        return None

    return bs4.BeautifulSoup(response.text, "html.parser")


def get_years_and_details(events_page):
    stars_nodes = events_page.select(".eventlist-event .star-count")
    years_nodes = [node.parent for node in stars_nodes]
    years_and_stars = [
        (year, stars)
        for year, stars in filter(None, map(get_year_and_stars, years_nodes))
        if stars
    ]
    return {
        str(year): {
            "stars": stars,
            "days": get_year_day_stars(year),
        }
        for year, stars in years_and_stars
    }


def get_total_stars(events_page):
    total_stars_nodes = events_page.select("p > .star-count")
    return parse_star_count(total_stars_nodes)


def get_user_name(events_page):
    user_nodes = events_page.select(".user")
    if not user_nodes:
        click.echo(
            f"Either the session ID in {e_error('AOC_SESSION_ID')} is wrong, "
            f"or it has expired: could not find the user name")
        return None

    user_node = user_nodes[0]
    text_children = [
        child
        for child in user_node.children
        if isinstance(child, str)
    ]
    if not text_children:
        click.echo(
            f"Either the user name is blank or the format has changed")
        return None
    return text_children[0].strip()


def get_year_day_stars(year):
    year_page = get_year_page(year)
    if year_page is None:
        return {}

    days_nodes = year_page.select('.calendar > a[class^="calendar-day"]')
    # noinspection PyTypeChecker
    return dict(filter(None, map(get_day_and_stars, days_nodes)))


def get_year_page(year):
    session_id = get_session_id()
    if not session_id:
        return None

    response = requests.get(
        f'https://adventofcode.com/{year}',
        cookies={"session": session_id},
        headers={"User-Agent": "aox"},
    )
    if not response.ok:
        click.echo(
            f"Could not get "
            f"{e_error(f'year {year} information')} from AOC "
            f"site (status was {e_error(str(response.status_code))}) - is the "
            f"internet down, AOC down, the URL is wrong, or are you banned?")
        return None

    return bs4.BeautifulSoup(response.text, "html.parser")


def get_day_and_stars(day_node):
    day_name_nodes = day_node.select(".calendar-day")
    if not day_name_nodes:
        return None
    day_name_node = day_name_nodes[0]
    day_text = day_name_node.text
    try:
        day = int(day_text)
    except ValueError:
        return None

    class_names = day_node.attrs['class']
    if 'calendar-verycomplete' in class_names:
        stars = 2
    elif 'calendar-complete' in class_names:
        stars = 1
    else:
        stars = 0

    return str(day), stars


def get_year_and_stars(year_node):
    year_name_node = year_node.findChild('a')
    if not year_name_node:
        return None
    year_name_match = re.compile(r'^\[(\d+)]$').match(year_name_node.text)
    if not year_name_match:
        return None
    year_text, = year_name_match.groups()
    year = int(year_text)

    stars_nodes = year_node.select('.star-count')
    stars = parse_star_count(stars_nodes, default=0)

    return year, stars


def parse_star_count(stars_nodes, default=None):
    if not stars_nodes:
        return default
    stars_node = stars_nodes[0]
    stars_match = re.compile(r'^(\d+)\*$').match(stars_node.text.strip())
    if not stars_match:
        return default

    stars_text, = stars_match.groups()
    return int(stars_text)


@aox.command()
@click.pass_context
def update_readme(ctx):
    readme_path = get_readme_path()
    if not readme_path:
        return
    combined_data = ctx.obj["combined_data"]
    if not combined_data["has_site_data"]:
        click.echo(
            f"Since {e_error('local site data')} are missing the "
            f"README {e_error('cannot be updated', fg='red')}: run "
            f"{e_suggest('aox fetch')} first")
        return

    readme_text = readme_path.read_text()

    from aox.summary.base_summary import summary_registry
    updated_readme_text = summary_registry.update_text(
        readme_text, combined_data)
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
