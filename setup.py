#!/usr/bin/env python
import os
from distutils.core import setup
from pathlib import Path

import setuptools

from aox.version import AOX_PACKAGE_VERSION_LABEL

current_directory = Path(os.path.dirname(os.path.realpath(__file__)))


setup(
    name='aox',
    version=AOX_PACKAGE_VERSION_LABEL,
    description='AdventOfCode Submissions Framework',
    author='Costas Basdekis',
    author_email='costas@basdekis.io',
    url='https://github.com/costas-basdekis/aox',
    long_description=current_directory.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(include=("aox*",)),
    scripts=[
        'scripts/aox',
    ],
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Typing :: Typed',
    ],
)
