import time
from typing import Callable, Iterator
from pystr.alphabet_string import String
from pystr.exact import bmh, bmh_b, bmh_alpha
from helpers import random_string

Algo = Callable[[str, str], Iterator[int]]


def bmh_b_wrap(x: str, p: str) -> Iterator[int]:
    yield from bmh_b(x.encode(), p.encode())


def bmh_alpha_wrap(x: str, p: str) -> Iterator[int]:
    xs = String(x)
    try:
        ps = String(p, xs.alpha)
    except KeyError:
        return
    yield from bmh_alpha(xs, ps)


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


print("BMH:      ", time_algo(bmh,            50000, 200, 10))
print("BMH-B:    ", time_algo(bmh_b_wrap,     50000, 200, 10))
print("BMH-Alpha:", time_algo(bmh_alpha_wrap, 50000, 200, 10))
