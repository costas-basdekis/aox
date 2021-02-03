import tempfile
from contextlib import nullcontext
from pathlib import Path
from unittest import TestCase

from aox.settings import get_settings
from aox.summary import BaseSummary, summary_registry
from tests.utils import using_controller, amending_settings


@summary_registry.register
class TestSummary(BaseSummary):
    marker_prefix = "test"

    def generate(self, combined_info):
        return (
            f"\n"
            f"Years: {min(combined_info.year_infos)}"
            f"-{min(max(combined_info.year_infos), 2020)}"
            f"\n"
        )


@summary_registry.register
class Test2Summary(BaseSummary):
    marker_prefix = "test2"

    def generate(self, combined_info):
        return (
            f"\n"
            f"Years #2: {min(combined_info.year_infos)}"
            f"-{min(max(combined_info.year_infos), 2020)}"
            f"\n"
        )


class TestControllerUpdateReadme(TestCase):
    def check_readme(self, parts_to_create_on_disk, collected_data,
                     initial_content, expected_content, expected_result):
        if initial_content is None:
            readme_file = nullcontext()
            new_settings = {"readme_path": None}
        else:
            readme_file = tempfile.NamedTemporaryFile(mode="w")
            new_settings = {"readme_path": Path(readme_file.name)}
        with using_controller(parts_to_create_on_disk, collected_data) \
                as (controller, _, _), readme_file, \
                amending_settings(**new_settings):
            if initial_content is not None:
                readme_file.write(initial_content)
                readme_file.flush()
            self.assertEqual(controller.update_readme(), expected_result)
            readme_path = get_settings().readme_path
            if readme_path and readme_path.exists():
                content = readme_path.read_text()
            else:
                content = None

            self.assertEqual(content, expected_content)

    def test_nothing_happens_with_no_readme_path(self):
        self.check_readme([], None, None, None, False)

    def test_doesnt_change_with_no_tags(self):
        self.check_readme(
            [], None,
            "A Readme with no tags\nMultiple lines of it\n",
            "A Readme with no tags\nMultiple lines of it\n",
            False,
        )

    def test_doesnt_change_with_no_matching_tags(self):
        self.check_readme(
            [], None,
            "A Readme with irrelevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (irrelevant-start)\n"
            "[//]: # (irrelevant-end)\n",
            "A Readme with irrelevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (irrelevant-start)\n"
            "[//]: # (irrelevant-end)\n",
            False,
        )

    def test_doesnt_change_with_no_site_data(self):
        self.check_readme(
            [], None,
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "[//]: # (test-end)\n",
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "[//]: # (test-end)\n",
            False,
        )

    def test_changes_with_site_data_and_relevant_tags(self):
        self.check_readme(
            [], {"username": "Test User", "total_stars": 0, "years": {}},
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "[//]: # (test-end)\n",
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n",
            True,
        )

    def test_changes_with_site_data_and_multiple_relevant_tags(self):
        self.check_readme(
            [], {"username": "Test User", "total_stars": 0, "years": {}},
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "[//]: # (test2-end)\n",
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "Years #2: 2015-2020\n"
            "[//]: # (test2-end)\n",
            True,
        )

    def test_doesnt_change_with_same_site_data_and_multiple_relevant_tags(self):
        self.check_readme(
            [], {"username": "Test User", "total_stars": 0, "years": {}},
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "Years #2: 2015-2020\n"
            "[//]: # (test2-end)\n",
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "Years #2: 2015-2020\n"
            "[//]: # (test2-end)\n",
            False,
        )

    def test_partial_changes_are_applied(self):
        self.check_readme(
            [], {"username": "Test User", "total_stars": 0, "years": {}},
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (irrelevant-start)\n"
            "[//]: # (irrelevant-end)\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "[//]: # (test2-end)\n",
            "A Readme with relevant tags\n"
            "Multiple lines of it\n"
            "[//]: # (irrelevant-start)\n"
            "[//]: # (irrelevant-end)\n"
            "[//]: # (test-start)\n"
            "Years: 2015-2020\n"
            "[//]: # (test-end)\n"
            "[//]: # (test2-start)\n"
            "Years #2: 2015-2020\n"
            "[//]: # (test2-end)\n",
            True,
        )
