from helpers import check_matches

from pystr import bwt
from pystr import alphabet
from pystr import sais
from pystr import approx


def test_bw_transform() -> None:
    x = "mississippi"
    b, alpha, _ = bwt.burrows_wheeler_transform(x)
    r = bwt.reverse_burrows_wheeler_transform(b)
    assert r[-1] == 0  # last symbol is sentinel
    assert alpha.revmap(r[:-1]) == x


def test_bw_transform_bytes() -> None:
    x_ = "mississippi"
    x, alpha = alphabet.Alphabet.mapped_string_with_sentinel(x_)
    b, _ = bwt.burrows_wheeler_transform_bytes(x, alpha)
    r = bwt.reverse_burrows_wheeler_transform(b)
    assert r[-1] == 0  # last symbol is sentinel
    assert alpha.revmap(r[:-1]) == x_


def test_ctable() -> None:
    x, alpha = alphabet.Alphabet.mapped_string_with_sentinel("aabca")
    ctab = bwt.CTable(x, len(alpha))
    assert ctab[0] == 0, "Nothing is smaller than the sentinel"
    assert ctab[1] == 1, "$ is smaller than 'a'"
    assert ctab[2] == 4, "$ + three 'a'"
    assert ctab[3] == 5, "$ + three 'a' + one 'b'"


def test_otable() -> None:
    x = "aabca"
    transformed, alpha, _ = bwt.burrows_wheeler_transform(x)
    assert transformed == bytearray([1, 3, 0, 1, 1, 2])

    otab = bwt.OTable(transformed, len(alpha))
    assert len(otab._tbl) == len(alpha) - 1
    assert len(otab._tbl[0]) == len(transformed)
    assert otab._tbl[0] == [1, 1, 1, 2, 3, 3], "a counts"
    assert otab._tbl[1] == [0, 0, 0, 0, 0, 1], "b counts"
    assert otab._tbl[2] == [0, 1, 1, 1, 1, 1], "c counts"


def test_mississippi() -> None:
    x = "mississippi"
    sa = sais.sais(x)
    for j in sa:
        print(x[j:])
    search = bwt.exact_preprocess(x)
    for p in ("si", "ppi", "ssi", "pip", "x", ""):
        matches = list(search(p))
        print(p, matches)
        check_matches(x, p, matches)
    # the empty string should give us the entire x includng sentinel
    assert len(list(search(""))) == len(x) + 1


def test_mississippi_aprox_0() -> None:
    x = "mississippi"
    search = bwt.approx_preprocess(x)
    for p in ("si", "ppi", "ssi", "pip", "x"):
        matches = list(search(p, 0))
        print(p, matches)
        check_matches(x, p, [idx for idx, _ in matches])


def test_mississippi_aprox_edit() -> None:
    x = "mississippi"
    search = bwt.approx_preprocess(x)
    for edits in [1, 2, 3]:
        for p in ("si", "ppi", "ssi", "pip", "x"):
            for pos, cigar in search(p, edits):
                align = approx.extract_alignment(x, p, pos, cigar)
                assert approx.count_edits(align) <= edits
