from helpers import check_matches
from pystr import bwt
from pystr.alphabet_string import String
from pystr.sais import sais_string


def test_bw_transform() -> None:
    x = "mississippi"
    b = bwt.bw_transform(x)
    print(b)
    y = bwt.bw_reverse(b)
    print(y)


def test_ctable() -> None:
    x = String("aabca")
    ctab = bwt.CTable(x)
    assert ctab[0] == 0, "Nothing is smaller than the sentinel"
    assert ctab[1] == 1, "$ is smaller than 'a'"
    assert ctab[2] == 4, "$ + three 'a'"
    assert ctab[3] == 5, "$ + three 'a' + one 'b'"


def test_otable() -> None:
    x = String("aabca")
    sa = sais_string(x)
    transformed = [bwt.bwt(x, sa, i) for i in range(len(x))]
    assert transformed == [1, 3, 0, 1, 1, 2]

    otab = bwt.OTable(x, sa)
    assert len(otab._tbl) == len(x.alpha) - 1
    assert len(otab._tbl[0]) == len(x)
    assert otab._tbl[0] == [1, 1, 1, 2, 3, 3], "a counts"
    assert otab._tbl[1] == [0, 0, 0, 0, 0, 1], "b counts"
    assert otab._tbl[2] == [0, 1, 1, 1, 1, 1], "c counts"


def test_mississippi() -> None:
    x = "mississippi"
    sa = sais_string(String(x))
    for j in sa:
        print(x[j:])
    search = bwt.preprocess(x)
    for p in ("si", "ppi", "ssi", "pip", "x", ""):
        matches = list(search(p))
        print(matches)
        check_matches(x, p, matches)
    # the empty string should give us the entire x includng sentinel
    assert len(list(search(""))) == len(x) + 1
