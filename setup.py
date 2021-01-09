#!/usr/bin/env python

from distutils.core import setup

setup(
    name='aox',
    version='0.1',
    description='AdventOfCode Submissions Framework',
    author='Costas Basdekis',
    author_email='costas@basdekis.io',
    url='https://github.com/costas-basdekis/aox',
    packages=['aox'],
    scripts=[
        'scripts/aox',
        'scripts/aox_cli.py',
    ],
)
