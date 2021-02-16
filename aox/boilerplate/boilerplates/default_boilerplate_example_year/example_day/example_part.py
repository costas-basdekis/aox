#!/usr/bin/env python3
from aox.challenge import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        42
        """


Challenge.main()
challenge = Challenge()
