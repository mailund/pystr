import sys

from helpers import random_string, check_sorted, check_matches

from pystr.suffixtree import SuffixTree
from pystr import naive_st_construction
from pystr import mccreight_st_construction

from typing import Callable


def mississippi_to_dot(constr: Callable[[str], SuffixTree]) -> None:
    st = constr("mississippi")
    print(st.to_dot(), file=sys.stdout)


def test_naive_to_dot():
    mississippi_to_dot(naive_st_construction)


def test_mccreight_to_dot():
    mississippi_to_dot(mccreight_st_construction)


def test_naive_sorted():
    for k in range(10):
        x = random_string(500)
        st = naive_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def test_mccreight_sorted():
    for k in range(10):
        x = random_string(500)
        st = mccreight_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def check_search_mississippi(constr: Callable[[str], SuffixTree]) -> None:
    x = "mississippi"
    st = constr(x)
    for p in ("ssi", "ppi", "si", "pip", "x", ""):
        check_matches(x, p, st.search(p))
    assert len(set(st.search(""))) == len(x)

    for p in ("ssi", "ppi", "si", ""):
        assert p in st
    for p in ("pip", "x"):
        assert p not in st


def test_search_mississippi_naive():
    check_search_mississippi(naive_st_construction)


def test_search_mississippi_mccreight():
    check_search_mississippi(mccreight_st_construction)