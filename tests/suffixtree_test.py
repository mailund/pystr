from helpers import random_string, check_sorted, check_matches

from pystr.suffixtree import SuffixTree
from pystr import naive_st_construction
from pystr import mccreight_st_construction
from pystr import lcp_st_construction
from pystr import sais
from pystr.lcp import lcp_from_sa

from typing import Callable


def mississippi_to_dot(constr: Callable[[str], SuffixTree]) -> None:
    st = constr("mississippi")
    print(st.to_dot())


def test_naive_to_dot() -> None:
    mississippi_to_dot(naive_st_construction)


def test_mccreight_to_dot() -> None:
    mississippi_to_dot(mccreight_st_construction)


def test_naive_sorted() -> None:
    for k in range(10):
        x = random_string(500)
        st = naive_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def test_mccreight_sorted() -> None:
    for k in range(10):
        x = random_string(500)
        st = mccreight_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def check_search_mississippi(
    constr: Callable[[str, bool], SuffixTree]
) -> None:
    x = "mississippi"
    st = constr(x, False)  # exclude sentinel this time...
    for p in ("ssi", "ppi", "si", "pip", "x", ""):
        check_matches(x, p, st.search(p))
    assert len(set(st.search(""))) == len(x)

    for p in ("ssi", "ppi", "si", ""):
        assert p in st
    for p in ("pip", "x"):
        assert p not in st


def test_search_mississippi_naive() -> None:
    check_search_mississippi(naive_st_construction)


def test_search_mississippi_mccreight() -> None:
    check_search_mississippi(mccreight_st_construction)


def lcp_construction_wrapper(x: str,
                             include_sentinel: bool = False
                             ) -> SuffixTree:
    sa = sais(x, include_sentinel=include_sentinel)
    lcp = lcp_from_sa(x, sa)
    return lcp_st_construction(x, sa, lcp)


def test_lcp_to_dot() -> None:
    mississippi_to_dot(lcp_construction_wrapper)


def test_lcp_sorted() -> None:
    for k in range(10):
        x = random_string(500)
        st = lcp_construction_wrapper(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def test_search_mississippi_lcp() -> None:
    check_search_mississippi(lcp_construction_wrapper)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
