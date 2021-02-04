from dataclasses import dataclass
from pathlib import Path

from aox.boilerplate import DefaultBoilerplate
from aox.utils import get_current_directory


current_directory = get_current_directory()


@dataclass
class DummyBoilerplate(DefaultBoilerplate):
    example_year_path = current_directory\
        .joinpath('test_boilerplate_example_year')
    example_day_path: Path = example_year_path.joinpath('test_example_day')
    example_part_path: Path = example_day_path.joinpath('test_example_part.py')
    example_input_path: Path = example_day_path.joinpath('input.txt')
