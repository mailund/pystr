from pystr.exact import naive, border, kmp, bmh
from pystr.bwt import bwt_search
from pystr.suffixtree import mccreight_st_construction as mccreight
from helpers import random_string, fibonacci_string, check_equal_matches
from helpers import pick_random_patterns, pick_random_patterns_len
from typing import Callable, Iterator


def suffix_tree_exact(x, p):
    yield from mccreight(x).search(p)


ALGOS = [
    naive, border, kmp, bmh,
    bwt_search,
    suffix_tree_exact,
]


def check_occurrences(x: str, p: str,
                      algo: Callable[[str, str], Iterator[int]]):
    print(f"Checking occurrences for {algo.__name__}")
    print(f"x = {repr(x)}; p = {repr(p)}")
    matches = algo(x, p)
    for i in matches:
        if x[i:i+len(p)] != p:
            print(
                f"Mismatch: x[{i}:{i+len(p)}] == {x[i:i+len(p)]} != p == {p}")  # noqal
        assert x[i:i+len(p)] == p


def test_simple():
    x = "aaabaaaxaaab"
    p = "aaab"
    check_occurrences(x, p, kmp)
    x = 'caddadccbadcbddac'
    p = 'bba'
    check_occurrences(x, p, kmp)
    x = 'abadabccaad'
    p = 'badabcc'
    check_occurrences(x, p, kmp)
    x = "abcabab"
    p = "ab"
    check_equal_matches(x, p, naive, kmp)
    x = "abcababab"
    p = "abab"
    print(list(naive(x, p)))
    print(list(kmp(x, p)))
    check_equal_matches(x, p, naive, kmp)


def check_exact_matching(algo: Callable[[str, str], Iterator[int]]):
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        for p in pick_random_patterns(x, 10):
            check_occurrences(x, p, algo)
        for p in pick_random_patterns_len(x, 10, 3):
            check_occurrences(x, p, algo)

    for n in range(10, 15):
        x = fibonacci_string(n)
        for p in pick_random_patterns(x, 10):
            check_occurrences(x, p, algo)


def test_occurrences():
    for algo in ALGOS:
        check_exact_matching(algo)


def test_equal_matches():
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        for p in pick_random_patterns(x, 10):
            check_equal_matches(x, p, *ALGOS)
        for p in pick_random_patterns_len(x, 10, 3):
            check_equal_matches(x, p, *ALGOS)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
