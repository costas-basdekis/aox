#!/usr/bin/env python

from distutils.core import setup

setup(
    name='aox',
    version='1.0',
    description='AdventOfCode Submissions Framework',
    author='Costas Basdekis',
    author_email='costas@basdekis.io',
    url='https://github.com/costas-basdekis/aox',
    packages=['aox'],
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
    ]
)
