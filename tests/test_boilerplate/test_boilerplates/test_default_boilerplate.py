import glob
import tempfile
from pathlib import Path
from unittest import TestCase

from aox.boilerplate import DefaultBoilerplate
from aox.utils import get_current_directory
from tests.utils import amending_settings

current_directory = get_current_directory()


class TestDefaultBoilerplate(TestCase):
    def test_get_part_filename_absolute_path_single_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_part_filename(2020, 5, 'a'),
                Path('/tmp/test-directory/year_2020/day_05/part_a.py'))
            self.assertEqual(
                DefaultBoilerplate().get_part_filename(2020, 5, 'b'),
                Path('/tmp/test-directory/year_2020/day_05/part_b.py'))

    def test_get_part_filename_absolute_path_double_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_part_filename(2020, 15, 'b'),
                Path('/tmp/test-directory/year_2020/day_15/part_b.py'))

    def test_get_day_input_filename_absolute_path_single_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_day_input_filename(2020, 5),
                Path('/tmp/test-directory/year_2020/day_05/input.txt'))

    def test_get_day_input_filename_absolute_path_double_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_day_input_filename(2020, 15),
                Path('/tmp/test-directory/year_2020/day_15/input.txt'))

    def test_get_day_directory_absolute_path_single_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_day_directory(2020, 5),
                Path('/tmp/test-directory/year_2020/day_05'))

    def test_get_day_directory_absolute_path_double_digit_day(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_day_directory(2020, 15),
                Path('/tmp/test-directory/year_2020/day_15'))

    def test_get_year_directory_absolute_path(self):
        with amending_settings(challenges_root=Path('/tmp/test-directory')):
            self.assertEqual(
                DefaultBoilerplate().get_year_directory(2020),
                Path('/tmp/test-directory/year_2020'))

    def test_get_part_module_name_top_level_single_digit_day(self):
        with amending_settings(challenges_module_name_root=None):
            self.assertEqual(
                DefaultBoilerplate().get_part_module_name(2020, 5, 'a'),
                'year_2020.day_05.part_a')

    def test_get_part_module_name_top_level_double_digit_day(self):
        with amending_settings(challenges_module_name_root=None):
            self.assertEqual(
                DefaultBoilerplate().get_part_module_name(2020, 15, 'a'),
                'year_2020.day_15.part_a')

    def test_get_part_module_name_custom_package_single_digit_day(self):
        with amending_settings(challenges_module_name_root='custom.package'):
            self.assertEqual(
                DefaultBoilerplate().get_part_module_name(2020, 5, 'a'),
                'custom.package.year_2020.day_05.part_a')

    def test_get_part_module_name_custom_package_double_digit_day(self):
        with amending_settings(challenges_module_name_root='custom.package'):
            self.assertEqual(
                DefaultBoilerplate().get_part_module_name(2020, 15, 'a'),
                'custom.package.year_2020.day_15.part_a')

    def test_create_part_a_single_digit_day(self):
        files_in_repo_before_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        with tempfile.TemporaryDirectory() as challenges_root:
            self.assertEqual(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True),
                [])
            with amending_settings(challenges_root=Path(challenges_root)):
                DefaultBoilerplate().create_part(2020, 5, 'a')
            self.assertEqual(set(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True)), {
                f"{challenges_root}/year_2020",
                f"{challenges_root}/year_2020/__init__.py",
                f"{challenges_root}/year_2020/day_05",
                f"{challenges_root}/year_2020/day_05/__init__.py",
                f"{challenges_root}/year_2020/day_05/part_a.py",
                f"{challenges_root}/year_2020/day_05/input.txt",
            })
        files_in_repo_after_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        self.assertEqual(
            files_in_repo_before_create, files_in_repo_after_create)

    def test_create_part_a_double_digit_day(self):
        files_in_repo_before_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        with tempfile.TemporaryDirectory() as challenges_root:
            self.assertEqual(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True),
                [])
            with amending_settings(challenges_root=Path(challenges_root)):
                DefaultBoilerplate().create_part(2020, 15, 'a')
            self.assertEqual(set(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True)), {
                f"{challenges_root}/year_2020",
                f"{challenges_root}/year_2020/__init__.py",
                f"{challenges_root}/year_2020/day_15",
                f"{challenges_root}/year_2020/day_15/__init__.py",
                f"{challenges_root}/year_2020/day_15/part_a.py",
                f"{challenges_root}/year_2020/day_15/input.txt",
            })
        files_in_repo_after_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        self.assertEqual(
            files_in_repo_before_create, files_in_repo_after_create)

    def test_create_part_b_single_digit_day(self):
        files_in_repo_before_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        with tempfile.TemporaryDirectory() as challenges_root:
            self.assertEqual(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True),
                [])
            with amending_settings(challenges_root=Path(challenges_root)):
                DefaultBoilerplate().create_part(2020, 5, 'b')
            self.assertEqual(set(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True)), {
                f"{challenges_root}/year_2020",
                f"{challenges_root}/year_2020/__init__.py",
                f"{challenges_root}/year_2020/day_05",
                f"{challenges_root}/year_2020/day_05/__init__.py",
                f"{challenges_root}/year_2020/day_05/part_a.py",
                f"{challenges_root}/year_2020/day_05/part_b.py",
                f"{challenges_root}/year_2020/day_05/input.txt",
            })
        files_in_repo_after_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        self.assertEqual(
            files_in_repo_before_create, files_in_repo_after_create)

    def test_create_part_b_double_digit_day(self):
        files_in_repo_before_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        with tempfile.TemporaryDirectory() as challenges_root:
            self.assertEqual(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True),
                [])
            with amending_settings(challenges_root=Path(challenges_root)):
                DefaultBoilerplate().create_part(2020, 15, 'b')
            self.assertEqual(set(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True)), {
                f"{challenges_root}/year_2020",
                f"{challenges_root}/year_2020/__init__.py",
                f"{challenges_root}/year_2020/day_15",
                f"{challenges_root}/year_2020/day_15/__init__.py",
                f"{challenges_root}/year_2020/day_15/part_a.py",
                f"{challenges_root}/year_2020/day_15/part_b.py",
                f"{challenges_root}/year_2020/day_15/input.txt",
            })
        files_in_repo_after_create = glob.glob(
            str(current_directory.joinpath('**/*')), recursive=True)
        self.assertEqual(
            files_in_repo_before_create, files_in_repo_after_create)

    def test_paths_in_created_part_b_single_digit_day(self):
        with tempfile.TemporaryDirectory() as challenges_root:
            with amending_settings(challenges_root=Path(challenges_root)):
                boilerplate = DefaultBoilerplate()
                boilerplate.create_part(2020, 5, 'b')
                paths = set(map(str, (
                    boilerplate.get_part_filename(2020, 5, 'a'),
                    boilerplate.get_part_filename(2020, 5, 'b'),
                    boilerplate.get_day_directory(2020, 5),
                    boilerplate.get_day_input_filename(2020, 5),
                    boilerplate.get_year_directory(2020),
                )))
            self.assertTrue(set(glob.glob(
                str(Path(challenges_root).joinpath('**/*')), recursive=True),
            ).issuperset(paths))
