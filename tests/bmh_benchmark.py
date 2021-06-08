import time
from typing import Callable, Iterator
from pystr.exact import bmh, bmh_b
from helpers import random_string

Algo = Callable[[str, str], Iterator[int]]


def bmh_wrap(x: str, p: str) -> Iterator[int]:
    yield from bmh_b(x.encode(), p.encode())


def consume(iter: Iterator[int]) -> None:
    for _ in iter:
        pass


def time_algo(algo: Algo, n: int, m: int, k: int) -> float:
    total = 0.0
    for _ in range(k):
        x = random_string(n, alpha="abcdefg")
        p = random_string(m, alpha="abcdefgh")
        now = time.time()
        consume(algo(x, p))
        total += time.time() - now
    return total


print("BMH:  ", time_algo(bmh,      50000, 200, 10))
print("BMH-B:", time_algo(bmh_wrap, 50000, 200, 10))
