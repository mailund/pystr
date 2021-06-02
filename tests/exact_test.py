from typing import Callable, Iterator

from pystr.exact import naive, border, kmp, bmh
from pystr.bwt import bwt_search
from pystr.suffixtree import mccreight_st_construction as mccreight

from helpers import random_string, fibonacci_string
from helpers import pick_random_patterns, pick_random_patterns_len, \
    pick_random_prefix, pick_random_suffix
from helpers import check_matches, check_equal_matches
from helpers import collect_tests


# wrapper
def suffix_tree_exact(x, p):
    yield from mccreight(x).search(p)


ALGOS = [
    naive, border, kmp, bmh,
    bwt_search,
    suffix_tree_exact,
]


def check_empty(algo):
    def test(_):
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


def check_exact_matching(algo: Callable[[str, str], Iterator[int]]):
    def test(_):
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


def check_against_naive(algo: Callable[[str, str], Iterator[int]]):
    def test(_):
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
