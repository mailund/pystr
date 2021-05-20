from helpers import check_matches
from collections.abc import Iterator
from pystr import skew
from pystr import CTAB, OTAB, c_table, o_table, bwt_search

BWTPreproc = tuple[list[int], CTAB, OTAB]


def preprocess(x: str, sa: list[int]) -> BWTPreproc:
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())
    return sa, ctab, otab


def search(x: str, p: str,
           sa: list[int], ctab: CTAB, otab: OTAB) -> Iterator[int]:
    L, R = bwt_search(x, p, ctab, otab)
    for i in range(L, R):
        yield sa[i]


def test_mississippi():
    x = "mississippi"
    sa = skew(x)
    prep = preprocess(x, sa)
    for p in ("ssi", "ppi", "si", "pip", "x", ""):
        matches = search(x, p, *prep)
        check_matches(x, p, matches)
    # the empty string should give us the entire x
    assert len(set(search(x, "", *prep))) == len(x)
