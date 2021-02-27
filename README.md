# aox - Python Advent of Code Submissions helper

![Tests](https://github.com/costas-basdekis/aox/workflows/Tests/badge.svg)
[![AOX version](https://pypip.in/v/aox/badge.png)](https://pypi.org/project/aox/)
![AOX downloads](https://pypip.in/d/aox/badge.png)

AOX was created with the following ideals:

1. I wanted to be able to run tests for each challenge
2. I didn't want to write the same code to load the input, run the tests, and
print the result
3. I wanted all of my challenges to have the same structure

The main feature of AOX is auto-creating the boilerplate for each challenge,

Currently only Python>=3.7 is supported.

[aoc]: https://adventofcode.com/

## Quick start

Install `aox` (Python>=3.7 needed):

```shell script
pip install aox
```

Create your settings:

```shell script
aox init-settings
```

Edit `.aox/sensitive_user_settings.py` to put your AOC session token

```python
# Copy-paste from your browser cookies
AOC_SESSION_ID = "..."
```

The following creates the boilerplate, and downloads your input:

```shell script
aox add 2020 1 a
```

Edit the file to solve the challenge (your input is automatically passed
in), and return the solution inside the `Challenge.solve` body:

```python
class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
         return your_awesome_calculations(_input)
```

If you want to check it works you can run it:

```shell script
aox challenge 2020 1 a run
```

When you're happy with the result, submit it:

```shell script
aox challenge 2020 1 a submit --yes
```

It will run your code, take the result, and submit it! If it's successful:
hurray! Time to solve part B with:

```shell script
aox add 2020 1 b
```

And so on

## Features

#### Custom boilerplate

If you always want to import certain libraries (eg `itertools`, `functools`,
your own `utils` library), you can create a template, so that you don't have to
write the same things again and again:
```python
#!/usr/bin/env python3
import aox.challenge
import my_useful_utils
import itertools, functools
import re


class Challenge(aox.challenge.BaseChallenge):
    ...

...
```

Check the [boilerplate customisation](#boilerplate-customisation) for more
details.

#### Testing, running, debugging, interactive challenges

I've found that writing small [doctests] makes it much easier to develop
solutions for AOC, especially when they become more complicated.

AOX automatically picks up all doctests in a challenge and runs them if you run
`aox challenge <year> <day> <part> test`.

It also prints your solution when you run
`aox challenge <year> <day> <part> run`. If you add the `--debug` flag, then you
can use the `debugger` parameter to your `Challenge.solve` method, which is
useful when you want to print diagnostic stats:
```python
class Challenge(BaseChallenge):
  def solve(self, _input, debugger):
    # Print something, if debugging is enable, and enough
    # time has passed from the previous print statement
    debugger.report_if(
        "Many many lines of debug information")
    # By default there is a 5s interval between printing
    # To change that, use the --debug-interval/-i flag
    debugger.report_if(
        "You won't see this")    
    # After enough time, `report_if` will print
    time.sleep(5)
    # To print something expensive, first check:
    if debugger.should_report():
      debugger.report(
        "Some expensive calculation:", expensive_calculation())
    # Debug through an iterable
    for index in range(10):
      debugger.step()
      debugger.report_if(f"looking at index {index}")
      ...
    # Also helpers to step through an iterable
    for index in debugger.stepping(range(10)):
      debugger.report_if(f"looking at index {index}")
      ...
    # Or through a while loop
    value = 0
    while debugger.step_if(value < 3):
      value += 1
      debugger.report_if(f"checking value {value}")
      ...
    return 6 * 7
```
To see more information check the [Debugger documentation]

`aox challenge <year> <day> <part> run` will print:
```
Solution: 42 (in 0.0s)
```
While `aox challenge <year> <day> <part> run --debug` will print:
```
Many many lines of debug information
That you don't want to read every time
Solution: 42 (in 0.0s)
```

Some challenges require you to interact with a program you're emulating, eg
[2019/15/A] or [2019/25/A], so before you write an automated solution, you might
elect to add an interactive mode. Other times, it's useful to be able to
interactively explore the problem space. To do that, simply add a `play` method
to your challenge, and run `aox challenge <year> <day> <part> play`:
```python
class Challenge(BaseChallenge):
  def play(self):
    _input = self.input
    while True:
      command = click.prompt("Enter u for up, d for down, q to quit")
      if command == 'u':
        ...
```

By default, if you don't specify a mode, AOX will first test and then run your
solution with `aox challenge <year> <day> <part>`:
```python
4 tests in 1 modules passed in 0.02s
Solution: 1234567 (in 0.0s)
```

[doctests]: https://docs.python.org/3/library/doctest.html
[2019/15/A]: https://adventofcode.com/2019/day/15
[2019/25/A]: https://adventofcode.com/2019/day/25
[Debugger documentation]: #debugging-your-code

#### Debugging your code

Sometimes you need to see some details about the process you're running, and
that could mean printing some info in the console, especially if you have a very
inefficient algorithm. The `Debugger` class, that is passed in as `debugger` in
the `Challenge.solve` method, provides some very useful functionality:

> `if debugger:` or `if debugger.enabled:`

This allows you to only do something if you passed `--debug`/`-d` as an argument

> `debugger.step_count`, `debugger.step_count_since_last_report`,
`debugger.step_frequency`, and `debugger.step_frequency_since_last_report`

You inspect how many steps total/per second have you performed since the
start/last time you reported.

> `if debugger.should_report(): debugger.report(...)` or
> `debugger.report_if(...)`

Advance the step count once, and print something to the console, if the debugger
is enabled, and enough time has passed since the last reporting (default is
`5s`, controlled by the `--debug-interval`/`-i` flag).

> `debugger.default_report()` and `debugger.default_report_if()`

Similar to the above, but it uses the formatting function from the
`DEFAULT_DEBUGGER_REPORT_FORMAT` to include some useful data in the output.

If your calculations run through nested function calls, you can also provide
additional info, by using `debugger.extra_report_formats`, or using the
`debugger.adding_extra_report_format` context manager:

```python
def level_1(data, debugger):
    def report_x(_, message):
        return f"x: {x}"
    # Will print: 'start x'
    debugger.default_report("start x")
    total = 0
    for x in range(10000000):
        with debugger.adding_extra_report_format(report_x):
            # Will print: 'x: 0, start y'
            debugger.default_report("start y")
            total += level_2(data[x], debugger)
def level_2(data, debugger):
    def report_y(_, message):
        return f"y: {y}"
    total = 0
    for y in range(10000000):
        with debugger.adding_extra_report_format(report_y):
            # Will print: 'x: 0, y: 0, start z'
            debugger.default_report("start z")
            total += level_3(data[y], debugger)
    return total
def level_3(data, debugger):
    total = 0
    for z in range(10000000):
        total += data[z]['a'] * data[z]['b']
        # Will print: 'x: 0, y: 0, z: 0'
        debugger.default_report_if(f"z: {z}")
    return total
```

> `debugger.duration_since_start` and `debugger.duration_since_last_report`, as
> well as `debugger.pretty_duration_*` and `debugger.get_pretty_duration_*()`

You can get the duration since the start/last report, which would be the number
of seconds since then. Since these are fine precision floats, you would like to
use the `pretty_*` property to get a nice `3h5m2s`
rendition of time, or the `get_pretty_*` methods to control how many `digits` do
of precision do you want to include in the seconds eg `3h5m2s.23`.

> `debugger.step()`, `debugger.stepping()`, and `debugger.step_if()`

It signifies that you have performed a number of steps (by default 1).

There are two helper methods:

```python3
# Step for each item in the passed in iterable
for item in debugger.stepping(['a', 'b', 'c']):
  ...

# Step for each truthy value
value = 0
while debugger.step_if(value < 3):
  value += 1
  ...
```

#### Reading your stars

To keep track how many and which stars you have, you can add your auth
credentials (check [Session Cookie](#session-cookie) for details), and use
`aox fetch` to refresh the stars cache. Then you can see them either via `aox`
or `aox list`:
```
Found 4 years with code and 162 stars:
  * 2020: 25 days with code and 50 stars
  * 2019: 25 days with code and 47 stars
  * 2018: 25 days with code and 34 stars
  * 2017: 25 days with code and 41 stars
```
Or for a particular year with `aox list 2019`:
```
Found 25 days with code in 2019 with 47 stars:
  * 25*!, 24**, 23**, 22*x, 21**, 20**, 19**, 18**, 17**, 16*x, 15**, 14**, 13**, 12**, 11**, 10**, 9**, 8**, 7**, 6**, 5**, 4**, 3**, 2**, 1**
```

#### Displaying your swag

You might be proud of how many stars you've gotten over the years, or you might
want to keep track of which challenges do you still have to solve. In any case,
AOX provides the ability to display star & code summaries in your README
automatically.

The way you can display these are customisable, by creating a new
`aox.summaries.BaseSummary` sub-class, and there are two default summaries
built-in:

**Event summary**

Simply add the following lines in your README:
```markdown
[//]: # (event-summary-start)
[//]: # (event-summary-end)
```

And after every `aox update-readme` you should see something like this:

| Total | 2020 | 2019 | 2018 | 2017 |
| --- | --- | --- | --- | --- |
| 162 :star: | 50 :star: :star: | 47 :star: | 34 :star: :star: | 41 :star: :star: |

**Submissions summary**

Add the following lines in your README:
```markdown
[//]: # (submissions-start)
[//]: # (submissions-end)
```

And after every `aox update-readme` you should see something like this:

|       | 2020                                                 | 2019                                                             |
|  ---: | :---:                                                | :---:                                                            |
|       | [Code][co-20]    &             [Challenges][ch-20]   | [Code][co-19]    &                         [Challenges][ch-19]   |
|       | 50 :star: :star:                                     | 47 :star: / 2 :x: / 1 :grey_exclamation:                         |
|  1    | [Code][co-20-01] :star: :star: [Challenge][ch-20-01] | [Code][co-19-01] :star: :star:             [Challenge][ch-19-01] |
|  2    | [Code][co-20-02] :star: :star: [Challenge][ch-20-02] | [Code][co-19-02] :star: :star:             [Challenge][ch-19-02] |
| ...   | ...                                                  | ...                                                              |
| 24    | [Code][co-20-24] :star: :star: [Challenge][ch-20-24] | [Code][co-19-24] :star: :star:             [Challenge][ch-19-24] |
| 25    | [Code][co-20-25] :star: :star: [Challenge][ch-20-25] | [Code][co-19-25] :star: :grey_exclamation: [Challenge][ch-19-25] |

**Your custom summary**

Simple override and register your summary class:
```python
from aox.summary import BaseSummary, summary_registry

@summary_registry.register
class MyCustomSummary(BaseSummary):
    # Don't forget to set your prefix
    marker_prefix = "my-custom"

    def generate(self, combined_info):
      years_with_stars_or_code = [
        year
        for year, year_info in combined_info.year_infos.items()
        if year_info.has_code or year_info.stars
      ]
      return (
        "Your custom markdown using stars & code info:\n"
        f"You have stars or code in {len(years_with_stars_or_code)} years\n"
        f"In 2020 you had {combined_info.year_infos[2020].stars} :star:\n"
      )
```

Don't forget to import your module, which can easily be done in your settings:
```python
EXTRA_MODULE_IMPORTS = ['my_custom_summary']
```

And to add the following lines in your README:
```markdown
[//]: # (my-custom-start)
[//]: # (my-custom-end)
```

And after every `aox update-readme` you should see something like this:

```markdown
Your custom markdown using stars & code info:
You have stars or code in 2 years
In 2020 you had 50 :star:
```

### Settings

After `aox init-settings`, you'll have an `.aox` folder in your repo:

```
.aox
├──.gitignore
├──sensitive_user_settings.py
├──site_data.json
└──user_settings.py
```

You should edit `sensitive_user_settings.py` to put the authentication cookie
for your account, to allow AOX access your AOC stats:

```python
AOC_SESSION_ID = (
    "a-very-long-hex-string"
    "that-you-can-get-from-your-browser"
)
```

You can find it in the `Application` tab (eg in Chrome), and you should not
commit that file in git, as it contains your secrets.

`site_data.json` is the cache of the AOC stars, from the last time you did
`aox fetch`. If you want all the data that AOX uses you can use `aox dump`.

Now, you can customise your experience in `user_settings.py`:

#### Session Cookie

Simply load it from your not-git-commited file
```python
AOC_SESSION_ID = sensitive_user_settings.AOC_SESSION_ID
```

#### Challenges code location

Where do your challenges live? The default boilerplate structure is
`<repo-root>/year_<year>/day_<day>/part_<part>.py`, so you don't have to change
this:
```python
CHALLENGES_ROOT = repo_root
CHALLENGES_MODULE_NAME_ROOT = None  # Top module
```
 If you want to use a different folder, eg
`<repo-root>/my/challenges/year_<year>/day_<day>/part_<part>.py`, you can do:
```python
CHALLENGES_ROOT = repo_root.joinpath('my', 'challenges')
CHALLENGES_MODULE_NAME_ROOT = 'my.challenges'  # Module prefix
```

#### Boilerplate customisation

By default, boilerplate is structure as mentioned above:
```python
CHALLENGES_BOILERPLATE = "aox.boilerplate.DefaultBoilerplate"
```

The most common use case is to create a template file with eg custom imports:
```python
#!/usr/bin/env python3
import aox.challenge
import my_useful_utils
import itertools, functools
import re


class Challenge(aox.challenge.BaseChallenge):
    ...

...
```
And then change the example part path:
```python
from aox.boilerplate import DefaultBoilerplate
CHALLENGES_BOILERPLATE = DefaultBoilerplate(
    example_part_path=repo_root.joinpath('my_custom_example_part.py'),
)
```
Or for more complex customisation, eg if you want a different structure (eg
`<repo-root>/<year>_<day>_<part>.py`), you can sub-class
`aox.boilerplate.BaseBoilerplate`, which AOX uses to know where to find your
code:
```python
import aox.boilerplate
class MyCustomBoilerplate(aox.boilerplate.DefaultBoilerplate):
    ...
```
And use it:
```python
CHALLENGES_BOILERPLATE = "my_custom_boilerplate.MyCustomBoilerplate"
```

#### Default format

To avoid repeating yourself every time you want to print something out, you can
define (or use the default) formatter function to add some standard details:

```python
def verbose_debugger_format(debugger: 'Debugger', message: str) -> str:
    return (
        f"Step: {debugger.step_count}, {message}, time: "
        f"{debugger.pretty_duration_since_start}, total steps/s: "
        f"{debugger.step_frequency}, recent steps/s: "
        f"{debugger.step_frequency_since_last_report}"
    )


DEFAULT_DEBUGGER_REPORT_FORMAT = verbose_debugger_format
```

If you want to customise it:

```python
def custom_debugger_format(debugger: 'Debugger', message: str) -> str:
    return (
        f"Custom format, delta time is "
        f"{debugger.pretty_duration_since_last_report} for {message}"
    )


DEFAULT_DEBUGGER_REPORT_FORMAT = custom_debugger_format
```

#### Site data cache

There is no reason to change this, and by default it lives in the `.aox` folder.
In case you want it somewhere else (eg your home directory), you can replace
this (remembering to use `Path`).
```python
# Save this info in my home directory
SITE_DATA_PATH = Path.home().joinpath('aoc_site_data.json')
```

#### README location

If you want AOX to put a summary of your stars in markdown, you can use this to
specify your README path
```python
README_PATH = repo_root.joinpath('README.md')
```

#### Custom settings

If you want to keep some extra settings, you can add them to
`.aox/user_settings.py`, and you can access them via the `settings.module`
attribute:

```python
MY_CUSTOM_SETTING = "foo"
```

```python
from aox.settings import settings_proxy
# Make sure to always use `settings_proxy()`
print(settings_proxy().module.MY_CUSTOM_SETTING)
```

## Contributing:

Please see the relevant section in [aox](./aox)
