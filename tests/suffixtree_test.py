from typing import Callable, Iterator

from pystr.suffixtree import SuffixTree
from pystr.exact import bmh
from pystr import naive_st_construction
from pystr import mccreight_st_construction
from pystr import lcp_st_construction
from pystr import sais
from pystr.lcp import lcp_from_sa

from helpers import fibonacci_string, random_string
from helpers import pick_random_patterns, pick_random_prefix,\
    pick_random_suffix, pick_random_patterns_len
from helpers import check_sorted, check_matches, check_equal_matches
from helpers import _Test, collect_tests

STConstructor = Callable[[str, bool], SuffixTree]


def lcp_construction_wrapper(x: str,
                             include_sentinel: bool = False
                             ) -> SuffixTree:
    sa = sais(x, include_sentinel=include_sentinel)
    lcp = lcp_from_sa(x, sa)
    return lcp_st_construction(x, sa, lcp)


ALGOS: list[STConstructor] = [
    naive_st_construction,
    mccreight_st_construction,
    lcp_construction_wrapper
]


def strip_algo_name(name: str) -> str:
    return name.split('_')[0]


def check_to_dot(x: str, algo: STConstructor) -> _Test:
    def test(_: object) -> None:
        algo(x, False).to_dot()
    return test


TestMississippiToDo = collect_tests(
    (strip_algo_name(algo.__name__), check_to_dot("mississippi", algo))
    for algo in ALGOS
)


def check_st_sorted(algo: STConstructor) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abc")
            # using the leaf iterator
            check_sorted(x, list(algo(x, False).root))
            check_sorted(x, list(algo(x, True).root))
        for f in range(5, 10):
            x = fibonacci_string(f)
            check_sorted(x, list(algo(x, False).root))
            check_sorted(x, list(algo(x, True).root))
        for n in range(5, 50):
            x = 'a' * n
            check_sorted(x, list(algo(x, False).root))
            check_sorted(x, list(algo(x, True).root))
    return test


TestSorted = collect_tests(
    (strip_algo_name(algo.__name__), check_st_sorted(algo))
    for algo in ALGOS
)


def check_equal_mccreight(algo: STConstructor) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abc")
            assert mccreight_st_construction(x, False) == algo(x, False)
            assert mccreight_st_construction(x, True) == algo(x, True)
        for f in range(5, 10):
            x = fibonacci_string(f)
            assert mccreight_st_construction(x, False) == algo(x, False)
            assert mccreight_st_construction(x, True) == algo(x, True)
        for n in range(5, 50):
            x = 'a' * n
            assert mccreight_st_construction(x, False) == algo(x, False)
            assert mccreight_st_construction(x, True) == algo(x, True)
    return test


TestEqualMcCreight = collect_tests(
    (strip_algo_name(algo.__name__), check_equal_mccreight(algo))
    for algo in ALGOS
)


def check_occurrences(algo: STConstructor) -> _Test:
    def st_search(x: str, p: str) -> Iterator[int]:
        return algo(x, True).search(p)

    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(50, alpha="abcd")
            for p in pick_random_patterns(x, 10):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_patterns_len(x, 10, 3):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_prefix(x, 10):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_suffix(x, 10):
                check_matches(x, p, st_search(x, p))
    return test


TestMatches = collect_tests(
    (strip_algo_name(algo.__name__), check_occurrences(algo))
    for algo in ALGOS
)


def check_against_bmh(algo: STConstructor) -> _Test:
    def st_search(x: str, p: str) -> Iterator[int]:
        print(algo(x, True).search(p))
        print(list(algo(x, True).search(p)))
        return algo(x, True).search(p)

    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(50, alpha="abcd")
            for p in pick_random_patterns(x, 10):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_patterns_len(x, 10, 3):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_prefix(x, 10):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_suffix(x, 10):
                check_equal_matches(x, p, bmh, st_search)
    return test


TestAgainstBMH = collect_tests(
    (strip_algo_name(algo.__name__), check_against_bmh(algo))
    for algo in ALGOS
)
