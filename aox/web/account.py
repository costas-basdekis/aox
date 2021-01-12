import re
from dataclasses import dataclass, field

import click

from aox.styling.shortcuts import e_error
from aox.web.aoc import WebAoc


__all__ = ['AccountScraper']


@dataclass
class AccountScraper:
    web_aoc: WebAoc = field(default_factory=WebAoc)

    def collect_data(self):
        events_page = self.web_aoc.get_events_page()
        if not events_page:
            return None

        username = self.get_username(events_page)
        if not username:
            return None

        total_stars = self.get_total_stars(events_page)

        collected_data = {
            "username": username,
            "total_stars": total_stars,
            "years": {},
        }

        for year, stars in self.get_years_stars(events_page).items():
            year_data = self.collect_year(year, stars)
            if year_data is None:
                continue
            collected_data["years"][year] = year_data
        return collected_data

    def get_username(self, events_page):
        """
        Extract the username. If there isn't a username, there is no information
        to gather.
        """
        user_nodes = events_page.select(".user")
        if not user_nodes:
            click.echo(
                f"Either the session ID in {e_error('AOC_SESSION_ID')} is "
                f"wrong, or it has expired: could not find the user name")
            return None

        user_node = user_nodes[0]
        text_children = [
            child
            for child in user_node.children
            if isinstance(child, str)
        ]
        if not text_children:
            click.echo(
                f"Either the user name is blank or the format has changed")
            return None
        return text_children[0].strip()

    def get_total_stars(self, events_page):
        """Grab the total stars"""
        total_stars_nodes = events_page.select("p > .star-count")
        return self.parse_star_count(total_stars_nodes)

    re_stars = re.compile(r'^(\d+)\*$')

    def parse_star_count(self, stars_nodes, default=None):
        """Star counts are represented in the same way everywhere"""
        if not stars_nodes:
            return default
        stars_node = stars_nodes[0]
        stars_match = self.re_stars.match(stars_node.text.strip())
        if not stars_match:
            return default

        stars_text, = stars_match.groups()
        return int(stars_text)

    def get_years_stars(self, events_page):
        stars_nodes = events_page.select(".eventlist-event .star-count")
        years_nodes = [node.parent for node in stars_nodes]
        return {
            year: stars
            for year, stars
            in filter(None, map(self.get_year_stars, years_nodes))
            if stars
        }

    re_year = re.compile(r'^\[(\d+)]$')

    def get_year_stars(self, year_node):
        """Get the stars for a year from a year node in the events page"""
        year_name_node = year_node.findChild('a')
        if not year_name_node:
            return None
        year_name_match = self.re_year.match(year_name_node.text)
        if not year_name_match:
            return None
        year_text, = year_name_match.groups()
        year = int(year_text)

        stars_nodes = year_node.select('.star-count')
        stars = self.parse_star_count(stars_nodes, default=0)

        return year, stars

    def collect_year(self, year, stars):
        year_page = self.web_aoc.get_year_page(year)
        if year_page is None:
            return None
        year_data = {
            "year": year,
            "stars": stars,
            "days": {},
        }

        days_nodes = year_page.select(
            '.calendar > a[class^="calendar-day"]')
        for day_node in days_nodes:
            day, stars = self.collect_day(day_node)
            if (day, stars) == (None, None):
                continue
            year_data["days"][day] = stars

        return year_data

    def collect_day(self, day_node):
        day_name_nodes = day_node.select(".calendar-day")
        if not day_name_nodes:
            return None, None
        day_name_node = day_name_nodes[0]
        day_text = day_name_node.text
        try:
            day = int(day_text)
        except ValueError:
            return None, None

        class_names = day_node.attrs['class']
        if 'calendar-verycomplete' in class_names:
            stars = 2
        elif 'calendar-complete' in class_names:
            stars = 1
        else:
            stars = 0

        return day, stars
