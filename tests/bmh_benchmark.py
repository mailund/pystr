"""Benchmarking bmh."""

import time
from typing import Callable, Iterator

from helpers import random_string
from pystr.exact import bmh, bmh_alpha, bmh_b

Algo = Callable[[str, str], Iterator[int]]


def bmh_b_wrap(x: str, p: str) -> Iterator[int]:
    """Wrap bmh_b to exact interface."""
    yield from bmh_b(x.encode(), p.encode())


def consume(itr: Iterator[int]) -> None:
    """Read everything from an iterator."""
    for _ in itr:
        pass


def time_algo(algo: Algo, n: int, m: int, k: int) -> float:
    """Measure the time it takes to run an algorithm."""
    total = 0.0
    for _ in range(k):
        x = random_string(n, alpha="abcdefg")
        p = random_string(m, alpha="abcdefgh")
        now = time.time()
        consume(algo(x, p))
        total += time.time() - now
    return total


print("BMH:      ", time_algo(bmh,        50000, 200, 10))
print("BMH-B:    ", time_algo(bmh_b_wrap, 50000, 200, 10))
print("BMH-Alpha:", time_algo(bmh_alpha,  50000, 200, 10))
