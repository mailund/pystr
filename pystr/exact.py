# Simple exact matching algorithms
from typing import Iterator
from collections import defaultdict
from .border_array import strict_border_array


def naive(x: str, p: str) -> Iterator[int]:
    for i in range(len(x) - len(p) + 1):
        for j in range(len(p)):
            if x[i + j] != p[j]:
                break
        else:
            yield i


def border(x: str, p: str) -> Iterator[int]:
    # Doesn't handle empty patterns directly...
    # (There would be several special cases to handle)
    if not p:
        yield from range(len(x) + 1)
        return

    # Build the border array
    ba = strict_border_array(p)

    # Now search...
    b = 0
    for i in range(len(x)):
        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]


def kmp(x: str, p: str) -> Iterator[int]:
    ba = strict_border_array(p)
    i, j = 0, 0
    while i < len(x):
        while j < len(p) and i < len(x):
            if x[i] != p[j]:
                break
            i += 1
            j += 1

        if j == len(p):
            yield i - len(p)

        if j == 0:
            i += 1
        else:
            j = ba[j - 1]

    # If p is the empty string we have one more position to report
    if not p:
        yield len(x)


def bmh(x: str, p: str) -> Iterator[int]:
    # Can't handle empty strings directly
    if not p:
        yield from range(len(x) + 1)
        return

    jump: dict[str, int] = \
        defaultdict(lambda: len(p))
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
