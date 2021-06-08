from typing import Callable, Iterator

from pystr.exact import naive, border, kmp, bmh
from pystr.exact import bmh_b as _bmh_b
from pystr.bwt import bwt_search
from pystr.suffixtree import mccreight_st_construction as mccreight

from helpers import random_string, fibonacci_string
from helpers import pick_random_patterns, pick_random_patterns_len, \
    pick_random_prefix, pick_random_suffix
from helpers import check_matches, check_equal_matches
from helpers import collect_tests, _Test

Algo = Callable[[str, str], Iterator[int]]


# wrapper
def suffix_tree_exact(x: str, p: str) -> Iterator[int]:
    yield from mccreight(x).search(p)


# wrapper
def bmh_b(x: str, p: str) -> Iterator[int]:
    x_b = x.encode('ascii')
    p_b = p.encode('ascii')
    yield from _bmh_b(x_b, p_b)


ALGOS: list[Algo] = [
    naive, border, kmp, bmh, bmh_b,
    bwt_search,
    suffix_tree_exact,
]


def check_empty(algo: Algo) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(10)
            p = ""
            hits = list(sorted(algo(x, p)))
            assert hits == list(range(len(x) + 1))
    return test


TestEmptyPatterns = collect_tests(
    (algo.__name__, check_empty(algo))
    for algo in ALGOS
)


def check_exact_matching(algo: Algo) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(100, alpha="abcd")
            for p in pick_random_patterns(x, 10):
                check_matches(x, p, algo(x, p))
            for p in pick_random_patterns_len(x, 10, 3):
                check_matches(x, p, algo(x, p))
            for p in pick_random_prefix(x, 10):
                check_matches(x, p, algo(x, p))
            for p in pick_random_suffix(x, 10):
                check_matches(x, p, algo(x, p))

        for n in range(10, 15):
            x = fibonacci_string(n)
            for p in pick_random_patterns(x, 10):
                check_matches(x, p, algo(x, p))
            for p in pick_random_prefix(x, 10):
                check_matches(x, p, algo(x, p))
            for p in pick_random_suffix(x, 10):
                check_matches(x, p, algo(x, p))

    return test


TestExactMatching = collect_tests(
    (algo.__name__, check_exact_matching(algo))
    for algo in ALGOS
)


def check_against_naive(algo: Algo) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(50, alpha="abcd")
            for p in pick_random_patterns(x, 10):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_patterns_len(x, 10, 3):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_prefix(x, 10):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_suffix(x, 10):
                check_equal_matches(x, p, naive, algo)
    return test


TestAgainstNaive = collect_tests(
    (algo.__name__, check_against_naive(algo))
    for algo in ALGOS
)
