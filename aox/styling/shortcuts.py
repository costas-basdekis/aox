"""
Provide shortcuts for styling parts of text when interacting with the console.
"""

import functools

import click


def make_colour(**colour_kwargs):
    """Create a colour shortcut"""
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
