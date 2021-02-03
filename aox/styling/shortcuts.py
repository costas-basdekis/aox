"""
Provide shortcuts for styling parts of text when interacting with the console.
"""

import functools

import click


def make_colour(**colour_kwargs):
    """
    Create a colour shortcut

    >>> make_colour(fg='red')('hey')
    '\\x1b[31mhey\\x1b[0m'
    >>> make_colour(fg='red')('hey', fg='green')
    '\\x1b[32mhey\\x1b[0m'
    >>> make_colour(fg='red')('hey', bg='green')
    '\\x1b[31m\\x1b[42mhey\\x1b[0m'
    >>> make_colour(bold=True)('hey')
    '\\x1b[1mhey\\x1b[0m'
    >>> make_colour(underline=True)('hey')
    '\\x1b[4mhey\\x1b[0m'
    """
    @functools.wraps(click.style)
    def custom_style(*args, **kwargs):
        return click.style(*args, **{**colour_kwargs, **kwargs})

    return custom_style


e_error = make_colour(fg='red')
e_warn = make_colour(fg='yellow')
e_success = make_colour(fg='green')
e_unable = make_colour(fg='white')

e_star = make_colour(fg='bright_yellow')
e_value = make_colour(fg='blue', bold=True)
e_suggest = make_colour(fg='cyan', underline=True)
