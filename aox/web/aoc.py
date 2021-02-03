from dataclasses import dataclass, field
from typing import Optional

import bs4
import click
import requests

from aox.settings import settings_proxy
from aox.styling.shortcuts import e_error


__all__ = ['WebAoc']


@dataclass
class WebAoc:
    """
    Helper class that abstracts requests to the AOC site.

    The session ID is necessary before any request.
    """
    session_id: Optional[str] = field(
        default_factory=lambda: settings_proxy().aoc_session_id)

    root_url = 'https://adventofcode.com'
    headers = {
        "User-Agent": "aox",
    }
    cookies = {}

    def get_events_url(self):
        """
        >>> WebAoc('test-session').get_events_url()
        'https://adventofcode.com/events'
        """
        return f"{self.root_url}/events"

    def get_year_url(self, year):
        """
        >>> WebAoc('test-session').get_year_url(2020)
        'https://adventofcode.com/2020'
        """
        return f"{self.root_url}/{year}"

    def get_day_url(self, year, day):
        """
        >>> WebAoc('test-session').get_day_url(2020, 5)
        'https://adventofcode.com/2020/day/5'
        """
        return f"{self.root_url}/{year}/day/{day}"

    def get_input_url(self, year, day):
        """
        >>> WebAoc('test-session').get_input_url(2020, 5)
        'https://adventofcode.com/2020/day/5/input'
        """
        return f"{self.root_url}/{year}/day/{day}/input"

    def get_answer_url(self, year, day):
        """
        >>> WebAoc('test-session').get_answer_url(2020, 5)
        'https://adventofcode.com/2020/day/5/answer'
        """
        return f"{self.root_url}/{year}/day/{day}/answer"

    def is_configured(self):
        """
        >>> WebAoc('test-session').is_configured()
        True
        >>> WebAoc(None).is_configured()
        False
        >>> WebAoc('').is_configured()
        False
        """
        return bool(self.session_id)

    def get_events_page(self):
        """Get the page with stars per year"""
        return self.get_html(self.get_events_url(), 'events information')

    def get_year_page(self, year):
        """Get the page with stars per day"""
        return self.get_html(
            self.get_year_url(year), f"year {year} information")

    def get_input_page(self, year, day):
        """Get the input for a particular day"""
        return self.get_text(
            self.get_input_url(year, day), f"year {year} day {day} input")

    def submit_solution(self, year, day, part, solution):
        """Post a solution"""
        return self.post_html(
            self.get_answer_url(year, day), {
                "level": 1 if part == "a" else 2,
                "answer": solution,
            }, f"year {year} day {day} input")

    def get_html(self, url, parse_name, *args, **kwargs):
        """Get parsed HTML"""
        return self.get(
            url=url, parse_type='html', parse_name=parse_name,
            *args, **kwargs)

    def get_text(self, url, parse_name, *args, **kwargs):
        """Get raw text"""
        return self.get(
            url=url, parse_type='text', parse_name=parse_name,
            *args, **kwargs)

    def get(self, *args, **kwargs):
        """Get a page"""
        return self.fetch(requests.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        """Submit a request"""
        return self.fetch(requests.post, *args, **kwargs)

    def post_html(self, url, data, parse_name, *args, **kwargs):
        """Post and return parsed HTML"""
        return self.post(
            url=url, data=data, parse_type='html', parse_name=parse_name,
            *args, **kwargs)

    def fetch(self, method, url, extra_headers=None, extra_cookies=None,
              parse_type=None, parse_name=None, data=None):
        """
        Generic method for interacting with the site. It can also parse the the
        result as a particular type (eg HTML).
        """
        if not self.is_configured():
            return None

        if not url.startswith(self.root_url):
            raise Exception(
                f"Only AOC URLs can be accessed (starting with "
                f"'{self.root_url}'), not '{url}'")

        response = method(
            url,
            data=data,
            headers=self.get_headers(extra_headers),
            cookies=self.get_cookies(extra_cookies),
        )

        if parse_type:
            return self.parse(response, parse_type, parse_name)

        return response

    def get_headers(self, extra_headers=None):
        """
        Construct the headers for a request

        >>> WebAoc('test-session').get_headers()
        {'User-Agent': 'aox'}
        >>> WebAoc('test-session').get_headers({})
        {'User-Agent': 'aox'}
        >>> WebAoc('test-session').get_headers({'User-Agent': 'test'})
        {'User-Agent': 'test'}
        >>> WebAoc('test-session').get_headers(
        ...     {'User-Agent': 'test', 'foo': 'bar'})
        {'User-Agent': 'test', 'foo': 'bar'}
        """
        return {
            **self.headers,
            **(extra_headers or {}),
        }

    def get_cookies(self, extra_cookies=None):
        """
        Construct the cookies for a request

        >>> WebAoc('test-session').get_cookies()
        {'session': 'test-session'}
        >>> WebAoc('test-session').get_cookies({})
        {'session': 'test-session'}
        >>> WebAoc('test-session').get_cookies({'session': 'other'})
        {'session': 'other'}
        >>> WebAoc('test-session').get_cookies(
        ...     {'session': 'other', 'foo': 'bar'})
        {'session': 'other', 'foo': 'bar'}
        """
        return {
            "session": self.session_id,
            **self.cookies,
            **(extra_cookies or {}),
        }

    def parse(self, response, _type, name):
        """
        Parse a response as a particular type (eg HTML)

        >>> from requests import Response
        >>> _response = Response()
        >>> _response._content = b'<html><body><article>Hi'
        >>> _response.status_code = 200
        >>> html = WebAoc('test-session').parse(_response, 'html', 'test')
        >>> html
        <html><body><article>Hi</article></body></html>
        >>> html.article
        <article>Hi</article>
        >>> _response = Response()
        >>> _response._content = b'Hello there'
        >>> _response.status_code = 200
        >>> WebAoc('test-session').parse(_response, 'text', 'test')
        'Hello there'
        """
        if _type == 'html':
            return self.as_html(response, name)
        if _type == 'text':
            return self.as_text(response, name)
        else:
            raise Exception(f"Unknown parse type '{_type}'")

    def as_html(self, response, name):
        """
        Parse a response as HTML

        >>> from requests import Response
        >>> _response = Response()
        >>> _response._content = b'<html><body><article>Hi'
        >>> _response.status_code = 200
        >>> html = WebAoc('test-session').as_html(_response, 'test')
        >>> html
        <html><body><article>Hi</article></body></html>
        >>> html.article
        <article>Hi</article>
        >>> _response = Response()
        >>> _response._content = b'Oops'
        >>> _response.status_code = 400
        >>> WebAoc('test-session').as_html(_response, 'test')
        """
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
        """
        Parse a response as text

        >>> from requests import Response
        >>> _response = Response()
        >>> _response._content = b'Hello there'
        >>> _response.status_code = 200
        >>> WebAoc('test-session').as_text(_response, 'test')
        'Hello there'
        >>> _response = Response()
        >>> _response._content = b'Oops'
        >>> _response.status_code = 400
        >>> WebAoc('test-session').as_text(_response, 'test')
        """
        if not response:
            return None

        if not response.ok:
            click.echo(
                f"Could not get {e_error(name)} from the AOC site "
                f"({response.status_code}) - is the internet down, AOC down, "
                f"the URL is wrong, or are you banned?")
            return None

        return response.text
