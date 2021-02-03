# flake8: noqa E501
import glob
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase

from aox.boilerplate import DefaultBoilerplate
from aox.model import RepoInfo
from aox.settings import settings_proxy
from tests.utils import amending_settings


# noinspection DuplicatedCode
class TestRepoInfoFromDisk(TestCase):
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as challenges_root:
            with amending_settings(
                    challenges_root=Path(challenges_root),
                    challenges_boilerplate=DefaultBoilerplate()):
                current_year = datetime.now().year
                repo_info = RepoInfo.from_roots()

                self.assertFalse(repo_info.has_code)
                self.assertTrue(set(repo_info.year_infos).issuperset(
                    {2015, 2016, 2017, 2018, 2019, 2020}))
                self.assertEqual(
                    set(repo_info.year_infos),
                    set(range(2015, current_year + 1)))
                for year, year_info in repo_info.year_infos.items():
                    self.assertEqual(year_info.year, year)
                    self.assertFalse(year_info.has_code)
                    self.assertFalse(year_info.path.exists())
                    self.assertEqual(
                        set(year_info.day_infos), set(range(1, 26)))
                    for day, day_info in year_info.day_infos.items():
                        self.assertEqual(day_info.year_info, year_info)
                        self.assertEqual(day_info.year, year)
                        self.assertEqual(day_info.day, day)
                        self.assertFalse(day_info.has_code)
                        self.assertFalse(day_info.path.exists())
                        self.assertEqual(set(day_info.part_infos), {'a', 'b'})
                        for part, part_info in day_info.part_infos.items():
                            self.assertEqual(part_info.day_info, day_info)
                            self.assertEqual(part_info.year, year)
                            self.assertEqual(part_info.day, day)
                            self.assertEqual(part_info.part, part)
                            self.assertFalse(part_info.has_code)
                            self.assertFalse(part_info.path.exists())

    def test_some_parts_exist(self):
        with tempfile.TemporaryDirectory() as challenges_root:
            with amending_settings(
                    challenges_root=Path(challenges_root),
                    challenges_boilerplate=DefaultBoilerplate()):
                settings_proxy().challenges_boilerplate.create_part(2020, 1, 'b')
                settings_proxy().challenges_boilerplate.create_part(2020, 2, 'b')
                settings_proxy().challenges_boilerplate.create_part(2020, 3, 'b')
                settings_proxy().challenges_boilerplate.create_part(2020, 10, 'b')
                settings_proxy().challenges_boilerplate.create_part(2020, 11, 'a')
                settings_proxy().challenges_boilerplate.create_part(2019, 1, 'b')
                settings_proxy().challenges_boilerplate.create_part(2019, 3, 'a')
                settings_proxy().challenges_boilerplate.create_part(2019, 11, 'b')

                folder_contents = glob.glob(
                    f"{challenges_root}/**/*", recursive=True)

                repo_info = RepoInfo.from_roots()

                self.assertTrue(repo_info.has_code)
                self.assertTrue(set(repo_info.year_infos).issuperset(
                    {2015, 2016, 2017, 2018, 2019, 2020}))

                # Check years with code
                self.assertEqual({
                    year_info.year
                    for year_info in repo_info.year_infos.values()
                    if str(year_info.path) in folder_contents
                }, {2019, 2020})
                self.assertEqual({
                    year_info.year
                    for year_info in repo_info.year_infos.values()
                    if year_info.has_code
                }, {2019, 2020})
                self.assertEqual({
                    year_info.year
                    for year_info in repo_info.year_infos.values()
                    if year_info.path.exists()
                }, {2019, 2020})

                # Check days with code
                self.assertEqual({
                    (day_info.year, day_info.day)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    if str(day_info.path) in folder_contents
                }, {
                    (2020, 1), (2020, 2), (2020, 3), (2020, 10), (2020, 11),
                    (2019, 1), (2019, 3), (2019, 11),
                })
                self.assertEqual({
                    (day_info.year, day_info.day)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    if day_info.has_code
                }, {
                    (2020, 1), (2020, 2), (2020, 3), (2020, 10), (2020, 11),
                    (2019, 1), (2019, 3), (2019, 11),
                })
                self.assertEqual({
                    (day_info.year, day_info.day)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    if day_info.path.exists()
                }, {
                    (2020, 1), (2020, 2), (2020, 3), (2020, 10), (2020, 11),
                    (2019, 1), (2019, 3), (2019, 11),
                })

                # Check parts with code
                self.assertEqual({
                    (part_info.year, part_info.day, part_info.part)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    for part_info in day_info.part_infos.values()
                    if str(part_info.path) in folder_contents
                }, {
                    (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'),
                    (2020, 2, 'b'), (2020, 3, 'a'), (2020, 3, 'b'),
                    (2020, 10, 'a'), (2020, 10, 'b'), (2020, 11, 'a'),
                    (2019, 1, 'a'), (2019, 1, 'b'), (2019, 3, 'a'),
                    (2019, 11, 'a'), (2019, 11, 'b'),
                })
                self.assertEqual({
                    (part_info.year, part_info.day, part_info.part)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    for part_info in day_info.part_infos.values()
                    if part_info.has_code
                }, {
                    (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'),
                    (2020, 2, 'b'), (2020, 3, 'a'), (2020, 3, 'b'),
                    (2020, 10, 'a'), (2020, 10, 'b'), (2020, 11, 'a'),
                    (2019, 1, 'a'), (2019, 1, 'b'), (2019, 3, 'a'),
                    (2019, 11, 'a'), (2019, 11, 'b'),
                })
                self.assertEqual({
                    (part_info.year, part_info.day, part_info.part)
                    for year_info in repo_info.year_infos.values()
                    for day_info in year_info.day_infos.values()
                    for part_info in day_info.part_infos.values()
                    if part_info.path.exists()
                }, {
                    (2020, 1, 'a'), (2020, 1, 'b'), (2020, 2, 'a'),
                    (2020, 2, 'b'), (2020, 3, 'a'), (2020, 3, 'b'),
                    (2020, 10, 'a'), (2020, 10, 'b'), (2020, 11, 'a'),
                    (2019, 1, 'a'), (2019, 1, 'b'), (2019, 3, 'a'),
                    (2019, 11, 'a'), (2019, 11, 'b'),
                })

                for year, year_info in repo_info.year_infos.items():
                    self.assertEqual(year_info.year, year)
                    self.assertEqual(
                        set(year_info.day_infos), set(range(1, 26)))
                    for day, day_info in year_info.day_infos.items():
                        self.assertEqual(day_info.year_info, year_info)
                        self.assertEqual(day_info.year, year)
                        self.assertEqual(day_info.day, day)
                        self.assertEqual(set(day_info.part_infos), {'a', 'b'})
                        for part, part_info in day_info.part_infos.items():
                            self.assertEqual(part_info.day_info, day_info)
                            self.assertEqual(part_info.year, year)
                            self.assertEqual(part_info.day, day)
                            self.assertEqual(part_info.part, part)
