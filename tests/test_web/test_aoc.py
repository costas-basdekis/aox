from unittest import TestCase
from urllib.parse import parse_qs

import requests
import responses

from aox.utils import get_current_directory
from aox.web import WebAoc

current_directory = get_current_directory()
web_fixtures = current_directory.joinpath('web_fixtures')


class TestWebAocNamedResponses(TestCase):
    @responses.activate
    def test_get_events_page(self):
        responses.add(
            responses.GET, 'https://adventofcode.com/events',
            body=web_fixtures.joinpath('events.html').read_bytes(),
            status=200,
        )

        events_page = WebAoc('test-session').get_events_page()

        self.assertEqual(len(responses.calls), 1)
        self.assertIsNotNone(events_page)
        self.assertEqual(events_page.title.text, 'Events - Advent of Code 2020')
        self.assertEqual(events_page.select('.star-count')[-1].text, '39*')

    @responses.activate
    def test_get_year_page(self):
        responses.add(
            responses.GET, 'https://adventofcode.com/2020',
            body=web_fixtures.joinpath('2020.html').read_bytes(),
            status=200,
        )

        events_page = WebAoc('test-session').get_year_page(2020)

        self.assertEqual(len(responses.calls), 1)
        self.assertIsNotNone(events_page)
        self.assertEqual(events_page.title.text, 'Advent of Code 2020')
        self.assertEqual(
            events_page.select('.calendar-day1')[0].text,
            '              ..........|..........                 1 **')

    @responses.activate
    def test_get_input_page(self):
        responses.add(
            responses.GET, 'https://adventofcode.com/2020/day/5/input',
            body=web_fixtures.joinpath('2020_day_5_input.txt').read_bytes(),
            status=200,
        )

        day_5_input = WebAoc('test-session').get_input_page(2020, 5)

        self.assertEqual(day_5_input, 'Day 5 Input\n')

    @responses.activate
    def test_submit_solution(self):
        def submit_callback(request):
            self.assertIsNotNone(request.body)
            query = parse_qs(request.body)
            self.assertEqual(query, {'level': ['1'], 'answer': ['Solution']})

            return 200, {}, '<html><body><article>Correct!'

        responses.add_callback(
            responses.POST, 'https://adventofcode.com/2020/day/5/answer',
            callback=submit_callback,
            content_type='text/html',
        )

        answer_page = WebAoc('test-session')\
            .submit_solution(2020, 5, 'a', 'Solution')
        self.assertEqual(answer_page.article.text, 'Correct!')


class TestWebAocBaseFetching(TestCase):
    @responses.activate
    def test_fetch_doesnt_do_anything_without_session_id(self):
        self.assertIsNone(WebAoc(None).fetch(None, None))

    @responses.activate
    def test_fetch_does_not_accept_non_https_aoc_urls(self):
        with self.assertRaises(Exception):
            WebAoc('test-session')\
                .fetch(requests.get, 'http://adventofcode.com/')
        with self.assertRaises(Exception):
            WebAoc('test-session')\
                .fetch(requests.get, 'https://adventofcodes.com/')

        with self.assertRaises(Exception):
            WebAoc('test-session')\
                .fetch(requests.get, 'https://adventofcode.com.de/')
