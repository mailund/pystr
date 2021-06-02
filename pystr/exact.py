# Simple exact matching algorithms
from typing import Iterator
from collections import defaultdict
from .border_array import strict_border_array


def naive(x: str, p: str) -> Iterator[int]:
    # If we have an empty string, j is never set,
    # and that can mess up the progress text. So we
    # need to give it a value here, just for that special case.
    j = 0
    for i in range(len(x) - len(p) + 1):
        for j in range(len(p)):
            if x[i + j] != p[j]:
                break
        else:
            # We made it through without breaking...
            yield i


def border(x: str, p: str) -> Iterator[int]:
    # Doesn't handle empty patterns directly...
    if not p:
        return list(range(len(x) + 1))

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
    # Doesn't handle empty patterns directly...
    if not p:
        return list(range(len(x) + 1))

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


def bmh(x: str, p: str) -> Iterator[int]:

    jump: dict[str, int] = \
        defaultdict(lambda: len(p))
    for j in range(len(p) - 1):  # skip last index!
        jump[p[j]] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        i += jump[x[i + len(p) - 1]]
