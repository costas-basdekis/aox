import os
from pathlib import Path

current_directory = Path(os.path.dirname(os.path.realpath(__file__)))

AOC_SESSION_ID = None
"""
This is the `session` cookie, when you're logged in on the AOC website. You
should copy it here verbatim.
"""

CHALLENGES_ROOT = current_directory
"""
The directory where the challenges code is on.
"""

CHALLENGES_MODULE_NAME_ROOT = None
"""
The name of the module under which the challenges leave. If there is no parent
module (or it is the root one) you can leave it as `None`.
"""

SITE_DATA_PATH = current_directory.joinpath('site_data.json')
"""
The path for the cached data from the AOC site - this helps remember how many
stars you have, and also which challenges have you completed.

This needs to be a `Path` instance.
"""

README_PATH = current_directory.joinpath('README.md')
"""
The path for your README file, so that it can update the stats.

This needs to be a `Path` instance.
"""
