import _setup  # noqa: F401

from helpers import check_equal_matches, check_matches
from collections.abc import Iterator
from pystr import sais
from pystr.bwt import CTAB, OTAB, c_table, o_table, bwt_search_tbls
from pystr.bwt import bwt_search

BWTPreproc = tuple[list[int], CTAB, OTAB]


def preprocess(x: str, sa: list[int]) -> BWTPreproc:
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())
    return sa, ctab, otab


def search_tbls(x: str, p: str,
                sa: list[int], ctab: CTAB, otab: OTAB) -> Iterator[int]:
    L, R = bwt_search_tbls(x, p, ctab, otab)
    for i in range(L, R):
        yield sa[i]


def test_mississippi():
    x = "mississippi"
    sa = sais(x, include_sentinel=True)
    prep = preprocess(x, sa)
    for p in ("ssi", "ppi", "si", "pip", "x", ""):
        matches = search_tbls(x, p, *prep)
        check_matches(x, p, matches)
        check_equal_matches(x, p,
                            lambda x, p: search_tbls(x, p, *prep),
                            bwt_search)
    # the empty string should give us the entire x
    assert len(set(search_tbls(x, "", *prep))) == len(x)
