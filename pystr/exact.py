# Simple exact matching algorithms
from typing import Iterator


def naive(x: str, p: str) -> Iterator[int]:
    for i in range(len(x)):
        if x[i:i+len(p)] == p:
            yield i


def border(x: str, p: str) -> Iterator[int]:
    assert p, "Doesn't handle empty patterns"

    # Build the border array
    ba = [0] * len(p)
    for j in range(1, len(p)):
        b = ba[j - 1]
        while b > 0 and p[j] != p[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if p[j] == p[b] else 0

    # Now search...
    b = 0
    for i in range(len(x)):
        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]  # update the border so we don't look at p[b].
