# aox - Advent of Code Submissions helper

This is a framework to make it easier to develop solutions for [AOC], with some
useful features for writing and submitting.

[aoc]: https://adventofcode.com/

## Quick start

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
    def solve(self, _input, debug=False):
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

## Contributing:

### Testing

Testing is mostly done via [doctests], which are collected via [pytest]. To run
them you can use `make`:

```shell script
make test
```

[doctests]: https://docs.python.org/3/library/doctest.html
[pytest]: https://docs.pytest.org/en/stable/
