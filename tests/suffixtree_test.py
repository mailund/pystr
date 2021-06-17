from typing import Callable, Iterator

from pystr.alphabet import Alphabet
from pystr.suffixtree import SuffixTree, Inner, Leaf
from pystr.exact import bmh
from pystr.suffixtree import naive_st_construction
from pystr.suffixtree import mccreight_st_construction
from pystr.suffixtree import lcp_st_construction
from pystr.sais import sais
from pystr.lcp import lcp_from_sa

from helpers import fibonacci_string, random_string
from helpers import pick_random_patterns, pick_random_prefix,\
    pick_random_suffix, pick_random_patterns_len
from helpers import check_sorted, check_matches, check_equal_matches
from helpers import _Test, collect_tests

STConstructor = Callable[[str], SuffixTree]


def lcp_construction_wrapper(x: str) -> SuffixTree:
    sa = sais(x)
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
        algo(x).to_dot()
    return test


TestMississippiToDo = collect_tests(
    (strip_algo_name(algo.__name__), check_to_dot("mississippi", algo))
    for algo in ALGOS
)


def test_contains() -> None:
    st = mccreight_st_construction("mississippi")
    assert "iss" in st
    assert "sss" not in st
    assert "ip" in st
    assert "x" not in st


def check_st_sorted(algo: STConstructor) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abc")
            # using the leaf iterator
            check_sorted(x, list(algo(x).root))
        for f in range(5, 10):
            x = fibonacci_string(f)
            check_sorted(x, list(algo(x).root))
        for n in range(5, 50):
            x = 'a' * n
            check_sorted(x, list(algo(x).root))
    return test


TestSorted = collect_tests(
    (strip_algo_name(algo.__name__), check_st_sorted(algo))
    for algo in ALGOS
)


def test_node_comparison() -> None:
    foo, _ = Alphabet.mapped_subseq("foo")
    bar, _ = Alphabet.mapped_subseq("bar")
    assert Leaf(0, foo) == Leaf(0, foo)
    assert Leaf(0, foo) != Leaf(1, foo)
    assert Leaf(0, foo) != Leaf(0, bar)

    assert Inner(foo) == Inner(foo)
    assert Inner(foo) != Inner(bar)

    i1 = Inner(foo)
    i2 = Inner(foo)
    assert i1 == i2
    i1.add_children(Leaf(0, bar))
    assert i1 != i2
    i2.add_children(Leaf(0, bar))
    assert i1 == i2


def check_equal_mccreight(algo: STConstructor) -> _Test:
    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(20, alpha="abc")
            assert mccreight_st_construction(x) == algo(x)
        for f in range(5, 10):
            x = fibonacci_string(f)
            assert mccreight_st_construction(x) == algo(x)
        for n in range(5, 50):
            x = 'a' * n
            assert mccreight_st_construction(x) == algo(x)
    return test


TestEqualMcCreight = collect_tests(
    (strip_algo_name(algo.__name__), check_equal_mccreight(algo))
    for algo in ALGOS
)


def check_occurrences(algo: STConstructor) -> _Test:
    def st_search(x: str, p: str) -> Iterator[int]:
        return algo(x).search(p)

    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(50, alpha="abcd")
            for p in pick_random_patterns(x, 5):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_patterns_len(x, 5, 3):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_prefix(x, 5):
                check_matches(x, p, st_search(x, p))
            for p in pick_random_suffix(x, 5):
                check_matches(x, p, st_search(x, p))
    return test


TestMatches = collect_tests(
    (strip_algo_name(algo.__name__), check_occurrences(algo))
    for algo in ALGOS
)


def check_against_bmh(algo: STConstructor) -> _Test:
    def st_search(x: str, p: str) -> Iterator[int]:
        print(algo(x).search(p))
        print(list(algo(x).search(p)))
        return algo(x).search(p)

    def test(_: object) -> None:
        for _ in range(10):
            x = random_string(50, alpha="abcd")
            for p in pick_random_patterns(x, 5):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_patterns_len(x, 5, 3):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_prefix(x, 5):
                check_equal_matches(x, p, bmh, st_search)
            for p in pick_random_suffix(x, 5):
                check_equal_matches(x, p, bmh, st_search)
    return test


TestAgainstBMH = collect_tests(
    (strip_algo_name(algo.__name__), check_against_bmh(algo))
    for algo in ALGOS
)
