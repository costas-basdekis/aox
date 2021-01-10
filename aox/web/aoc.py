from dataclasses import dataclass, field
from typing import Optional

import bs4
import click
import requests

from aox.settings import settings
from aox.styling.shortcuts import e_error


__all__ = ['WebAoc']


@dataclass
class WebAoc:
    """
    Helper class that abstracts requests to the AOC site.

    The session ID is necessary before any request.
    """
    session_id: Optional[str] = field(
        default_factory=lambda: settings.aoc_session_id)

    root_url = 'https://adventofcode.com'
    headers = {
        "User-Agent": "aox",
    }
    cookies = {}

    def is_configured(self):
        return bool(self.session_id)

    def get_events_page(self):
        """Get the page with stars per year"""
        return self.get_html('events', 'events information')

    def get_year_page(self, year):
        """Get the page with stars per day"""
        return self.get_html(f"{year}", f"year {year} information")

    def get_input_page(self, year, day):
        """Get the input for a particular day"""
        return self.get_text(
            f"{year}/day/{day}/input", f"year {year} day {day} input")

    def submit_solution(self, year, day, part, solution):
        """Post a solution"""
        return self.post_html(
            f"{year}/day/{day}/answer", {
                "level": 1 if part == "a" else 2,
                "answer": solution,
            }, f"year {year} day {day} input")

    def get_html(self, path, parse_name, *args, **kwargs):
        """Get parsed HTML"""
        return self.get(
            path=path, parse_type='html', parse_name=parse_name,
            *args, **kwargs)

    def get_text(self, path, parse_name, *args, **kwargs):
        """Get raw text"""
        return self.get(
            path=path, parse_type='text', parse_name=parse_name,
            *args, **kwargs)

    def get(self, *args, **kwargs):
        """Get a page"""
        return self.fetch(requests.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        """Submit a request"""
        return self.fetch(requests.post, *args, **kwargs)

    def post_html(self, path, data, parse_name, *args, **kwargs):
        """Post and return parsed HTML"""
        return self.post(
            path=path, data=data, parse_type='html', parse_name=parse_name,
            *args, **kwargs)

    def fetch(self, method, path, extra_headers=None, extra_cookies=None,
              parse_type=None, parse_name=None, data=None):
        """
        Generic method for interacting with the site. It can also parse the the
        result as a particular type (eg HTML).
        """
        if not self.is_configured():
            return None

        response = method(
            f"{self.root_url}/{path}",
            data=data,
            headers=self.get_headers(extra_headers),
            cookies=self.get_cookies(extra_cookies),
        )

        if parse_type:
            return self.parse(response, parse_type, parse_name)

        return response

    def get_headers(self, extra_headers=None):
        """Construct the headers for a request"""
        return {
            **self.headers,
            **(extra_headers or {}),
        }

    def get_cookies(self, extra_cookies=None):
        """Construct the cookies for a request"""
        return {
            "session": self.session_id,
            **self.cookies,
            **(extra_cookies or {}),
        }

    def parse(self, response, _type, name):
        """Parse a response as a particular type (eg HTML)"""
        if _type == 'html':
            return self.as_html(response, name)
        if _type == 'text':
            return self.as_text(response, name)
        else:
            raise Exception(f"Unknown parse type '{_type}'")

    def as_html(self, response, name):
        """Parse a response as HTML"""
        if not response:
            return None

        if not response.ok:
            click.echo(
                f"Could not get {e_error(name)} from the AOC site "
                f"({response.status_code}) - is the internet down, AOC down, "
                f"the URL is wrong, or are you banned?")
            return None

        return bs4.BeautifulSoup(response.text, "html.parser")

    def as_text(self, response, name):
        """Parse a response as text"""
        if not response:
            return None

        if not response.ok:
            click.echo(
                f"Could not get {e_error(name)} from the AOC site "
                f"({response.status_code}) - is the internet down, AOC down, "
                f"the URL is wrong, or are you banned?")
            return None

        return response.text
