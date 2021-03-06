"""Simple exact matching algorithms."""

import collections
import typing

from .alphabet import Alphabet
from .border_array import border_array, strict_border_array


def naive(x: str, p: str) -> typing.Iterator[int]:
    """Naive squared-time exact search algorithm."""
    for i in range(len(x) - len(p) + 1):
        for j, a in enumerate(p):
            if x[i + j] != a:
                break
        else:
            yield i


def border(x: str, p: str) -> typing.Iterator[int]:
    """Search algorithm based on the border array."""
    # Doesn't handle empty patterns directly...
    # (There would be several special cases to handle)
    if not p:
        yield from range(len(x) + 1)
        return

    # Build the border array
    ba = border_array(p)

    # Now search...
    b = 0
    for i, a in enumerate(x):
        while b > 0 and p[b] != a:
            b = ba[b - 1]
        b = b + 1 if p[b] == a else 0
        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]


def kmp(x: str, p: str) -> typing.Iterator[int]:
    """Run the Knuth-Morris-Pratt algorithm."""
    if not p:
        yield from range(len(x) + 1)
        return

    j = 0
    ba = strict_border_array(p)
    for i, a in enumerate(x):
        # shift down pattern...
        while a != p[j] and j > 0:
            j = ba[j - 1]

        # match one up, if we can...
        if a == p[j]:
            j += 1
            if j == len(p):
                yield i - len(p) + 1
                j = ba[j - 1]


def bmh(x: str, p: str) -> typing.Iterator[int]:
    """Run the Boyer-Moore-Horspool algorithm."""
    # Can't handle empty strings directly
    if not p:
        yield from range(len(x) + 1)
        return

    jump: dict[str, int] = collections.defaultdict(lambda: len(p))
    for j, a in enumerate(p[:-1]):  # skip last index!
        jump[a] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        i += jump[x[i + len(p) - 1]]


def bmh_b(x: bytes, p: bytes) -> typing.Iterator[int]:
    """Run the Boyer-Moore-Horspool algorithm."""
    # Can't handle empty strings directly
    if not p:
        yield from range(len(x) + 1)
        return

    jump: list[int] = [len(p)] * 256  # 256 different bytes
    for j, a in enumerate(p[:-1]):  # skip last index!
        jump[a] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        i += jump[x[i + len(p) - 1]]


# If p has the sentinel, it can only match the end of x.
# The function assumes that you don't have sentinels you do not
# want.
def bmh_alpha(x_: str, p_: str) -> typing.Iterator[int]:
    """Run the Boyer-Moore-Horspool algorithm."""
    x, alpha = Alphabet.mapped_string(x_)
    try:
        p = alpha.map(p_)
    except KeyError:
        # If we can't map, we can't have a hit
        return

    # Can't handle empty strings directly
    if not p:
        yield from range(len(x) + 1)
        return

    jump: list[int] = [len(p)] * len(alpha)
    # Strings don't alow slicing outside the valid range
    # so the p[:-1] trick isn't safe if len(p) == 1.
    # It's a design choice; I'd rather have errors than
    # silent unexpected behaviour.
    for j in range(len(p) - 1):
        jump[p[j]] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        i += jump[x[i + len(p) - 1]]
