# Simple exact matching algorithms
from typing import Iterator
from .border_array import border_array
from .output import show_prefix_next_comp, show_prefix_mismatch
from .cols import bright_green, bright_blue


def naive(x: str, p: str) -> Iterator[int]:
    for i in range(len(x)):
        if x[i:i+len(p)] == p:  # This always takes time O(len(p))!
            yield i


def border(x: str, p: str, progress=False) -> Iterator[int]:
    assert p, "Doesn't handle empty patterns"

    # Build the border array
    ba = border_array(p)

    # Now search...
    b = 0
    for i in range(len(x)):
        if progress:
            print(f"Iteration {bright_blue(i)}")
            show_prefix_next_comp(x, p, i - b, i - b)

        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        if progress:
            if b < len(p) and (i + b) < len(x) and x[i+b] == p[b]:
                show_prefix_next_comp(x, p, i, i - b)
            else:
                show_prefix_mismatch(x, p, i, i - b)
            if b == len(p):
                print(bright_green(f"Found pattern at index {i - len(p)}"))
                print()

        if b == len(p):
            yield i - len(p) + 1
            # update the border so we don't look at p[b].
            b = ba[b - 1]


def kmp(x: str, p: str, progress=False) -> Iterator[int]:
    ba = border_array(p)
    i, j = 0, 0
    while i < len(x):
        if progress:
            show_prefix_next_comp(x, p, i, j)

        while j < len(p) and i < len(x):
            if x[i] != p[j]:
                break
            i += 1
            j += 1

        if j == len(p):
            yield i - len(p)

        if progress:
            show_prefix_mismatch(x, p, i, j)
            if j == len(p):
                print(bright_green(f"Found pattern at index {i - len(p)}"))
                print()

        if j == 0:
            i += 1
        else:
            j = ba[j - 1]
