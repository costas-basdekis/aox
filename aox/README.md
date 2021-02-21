# AOX Structure
AOX started as a few scripts/functions to manage my own submissions repo, but
has now evolved to have a bit more universal appeal

## Ideals

### User ideals
1. Make it very easy for a coder to develop solutions
2. Don't be opinionated: provide reasonable defaults, but don't assume my way is
the universally best way. 
3. Be open for extension by default
4. It should 

### Development ideals
1. Prefer class-based OOP over function-based procedural
2. Define clear interfaces for moddable behaviour
3. Make code easily testable, including command-line

## Modules

### Controller
The main class is `Controller` in the [aox.controller.controller]
module, and provides functionality or access to functionality for achieving
everything that is necessary.

### CLI & scripts
The main user interface is a CLI tool using [click] in
[aox.command_line.command], and it should use exclusively `Controller` to issue
commands. The user will mainly use the `aox` command line script in the
[scripts] top-level directory

### Models
The data is split into two domains:
1. Local code management via `RepoInfo` in [aox.model.repo_info]
2. Remote stars retrieval via `AccountInfo` in [aox.model.account_info]

These are merged in `CombinedInfo` in [aox.model.combined_info]
that provides a unified view for every year/day/part.

### Settings
User choices are managed through `Settings` in [aox.settings.settings_class.py],
and access should only happen through the `settings_proxy` object, since
settings are initialised explicitly, and not at the start of the program.

### Boilerplate
Creation of boilerplate, and locating local challenges should happen through a
concrete instance of `BaseBoilerplate` in [aox.boilerplate.base_boilerplate.py].
A `DefaultBoilerplate` implementation is provided.

### AOC client
Interfacing with the AOC site should only happen through the facade methods of
`WebAoc` in [aox.web.aoc].

### Base challaenge
User code is accessed via subclassing `BaseChallenge` in
[aox.challenge.base_challenge], which `DefaultBoilerplate` includes.

### Summaries
Readme customisation is provided by different sub-classes of `BaseSummary` in
[aox.summary.base_summary.py], with some implementations in
[aox.summary.summaries].

### Utilities
Various utilities exist in [aox.utils], colouring shortcuts in
[aox.styling.shortcuts], and some advanced testing features in [aox.testing].

[click]: https://click.palletsprojects.com/en/7.x/
[aox.challenge.base_challenge]: ./challenge/base_challenge.py
[aox.command_line.command]: ./command_line/command.py
[aox.controller.controller]: ./controller/controller.py
[aox.model.account_info]: ./model/account_info.py
[aox.model.combined_info]: ./model/combined_info.py
[aox.model.repo_info]: ./model/repo_info.py
[aox.settings.settings_class.py]: ./settings/settings_class.py
[aox.styling.shortcuts]: ./styling/shortcuts.py
[aox.summary.base_summary.py]: ./summary/base_summary.py
[aox.summary.summaries]: ./summary/summaries
[aox.testing]: ./testing
[aox.utils]: ./utils
[aox.web.aoc]: ./web/aoc.py
[scripts]: ../scripts

# Contributing
## Testing

![Python package](https://github.com/costas-basdekis/aox/workflows/Python%20package/badge.svg)

Testing is mostly done via [doctests], which are collected via [pytest]. We also
use [flake8] (via [pytest-flake8]) to lint:

```shell script
make setup
make test
```

If you can use doctests inline in modules, and for more advance cases write unit
tests in [tests]

[doctests]: https://docs.python.org/3/library/doctest.html
[pytest]: https://docs.pytest.org/en/stable/
[flake8]: https://flake8.pycqa.org/en/3.1.1/index.html
[pytest-flake8]: https://pypi.org/project/pytest-flake8/
[tests]: ../tests

## Releasing
Before every release, the version should be incremented in [version.py]:
```python
AOX_VERSION = (1, 0, 2)
```

* Increment the patch part for non-breaking changes, that are not that
significant
* Increment the minor part for small breaking changes, and/or for mildly
interesting updates
* Increment the major part for drastic changes

There should be a single commit with the bumped version, and it should also be
tagged:
```shell script
make commit_and_tag
```

Then build and publish the PyPI package
```shell script
make build_and_publish
```

[version.py]: ./version.py
