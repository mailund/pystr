"""Test exact matching algorithms."""

from typing import Callable, Iterator

from helpers import (_Test, check_equal_matches, check_matches, collect_tests,
                     fibonacci_string, pick_random_patterns,
                     pick_random_patterns_len, pick_random_prefix,
                     pick_random_suffix, random_string)
from pystr.bwt import exact_preprocess
from pystr.exact import bmh, bmh_alpha
from pystr.exact import bmh_b as _bmh_b
from pystr.exact import border, kmp, naive
from pystr.suffixtree import mccreight_st_construction as mccreight

Algo = Callable[[str, str], Iterator[int]]


# wrapper
def suffix_tree_exact(x: str, p: str) -> Iterator[int]:
    """Exact search using a suffix tree."""
    yield from mccreight(x).search(p)


# wrapper
def bmh_b(x: str, p: str) -> Iterator[int]:
    """Search using the bmh_b algorithm."""
    x_b = x.encode('ascii')
    p_b = p.encode('ascii')
    yield from _bmh_b(x_b, p_b)


# wrapper
def bwt_search(x: str, p: str) -> Iterator[int]:
    """Search using the bwt/fmindex algorithm."""
    yield from exact_preprocess(x)(p)


ALGOS: list[Algo] = [
    naive, border, kmp,
    bmh, bmh_b, bmh_alpha,
    bwt_search,
    suffix_tree_exact,
]


def check_empty(algo: Algo) -> _Test:
    """Test if we can search for the empty string."""
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


def check_exact_matching(algo: Algo) -> _Test:   # noqa C901
    """Check that the algorithm does exact matching correct."""
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abcd")
            for _ in range(5):
                # allow characters not in x
                p = random_string(10, alpha="abef")
                check_matches(x, p, algo(x, p))
            for p in pick_random_patterns(x, 5):
                check_matches(x, p, algo(x, p))
            for p in pick_random_patterns_len(x, 5, 3):
                check_matches(x, p, algo(x, p))
            for p in pick_random_prefix(x, 5):
                check_matches(x, p, algo(x, p))
            for p in pick_random_suffix(x, 5):
                check_matches(x, p, algo(x, p))

        for n in range(5, 10):
            x = fibonacci_string(n)
            for p in pick_random_patterns(x, 5):
                check_matches(x, p, algo(x, p))
            for p in pick_random_prefix(x, 5):
                check_matches(x, p, algo(x, p))
            for p in pick_random_suffix(x, 5):
                check_matches(x, p, algo(x, p))

    return test


TestExactMatching = collect_tests(
    (algo.__name__, check_exact_matching(algo))
    for algo in ALGOS
)


def check_against_naive(algo: Algo) -> _Test:
    """Test if we get the same results as the naive algorithm."""
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abc")
            for p in pick_random_patterns(x, 5):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_patterns_len(x, 5, 3):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_prefix(x, 5):
                check_equal_matches(x, p, naive, algo)
            for p in pick_random_suffix(x, 5):
                check_equal_matches(x, p, naive, algo)
    return test


TestAgainstNaive = collect_tests(
    (algo.__name__, check_against_naive(algo))
    for algo in ALGOS
)
