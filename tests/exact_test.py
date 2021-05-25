from pystr.exact import naive, border
from pystr.bwt import bwt_search
from helpers import random_string, check_equal_matches
from helpers import pick_random_patterns, pick_random_patterns_len
from typing import Callable, Iterator


def check_occurrences(x: str, p: str, matches: Iterator[int]):
    for i in matches:
        assert x[i:i+len(p)] == p


def check_exact_matching(algo: Callable[[str, str], Iterator[int]]):
    x = random_string(100, alpha="abcd")
    for p in pick_random_patterns(x, 10):
        check_occurrences(x, p, algo(x, p))
    for p in pick_random_patterns_len(x, 10, 3):
        check_occurrences(x, p, algo(x, p))


def test_naive_occurrences():
    check_exact_matching(naive)


def test_border_occurrences():
    check_exact_matching(border)


def check_equal_algos(*algos: Callable[[str, str], Iterator[int]]):
    x = random_string(100, alpha="abcd")
    for p in pick_random_patterns(x, 10):
        check_equal_matches(x, p, *algos)
    for p in pick_random_patterns_len(x, 10, 3):
        check_equal_matches(x, p, *algos)


def test_equal_results():
    check_equal_algos(naive, border, bwt_search)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
