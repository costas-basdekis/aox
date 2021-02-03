import sys

__all__ = ['Literal']


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing import Any
    from collections import defaultdict
    Literal = defaultdict(lambda: Any)
