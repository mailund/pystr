from sais import map_string, classify_SL, is_LMS
from sais import sais
import BitVector as bv
from helpers import random_string, check_sorted


def test_remap():
    x = "mississippi"
    mapped, asize = map_string(x)
    assert mapped == [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    assert asize == 5

    for _ in range(10):
        x = random_string(1000)
        mapped, asize = map_string(x)
        assert set(mapped) == set(range(asize))


def test_classify():
    # mississippi$
    # LSLLSLLSLLLS
    x, _ = map_string("mississippi")
    assert len(x) == len("mississippi") + 1

    is_S = bv.BitVector(size=len(x))
    assert len(is_S) == len(x)

    classify_SL(is_S, x)

    expected = [
        # L    S     L      L      S     L      L
        False, True, False, False, True, False, False,
        # S   L      L      L      S
        True, False, False, False, True
    ]
    for i in range(len(is_S)):
        assert is_S[i] == expected[i]


def test_is_LMS():
    x, _ = map_string("mississippi")
    assert len(x) == len("mississippi") + 1
    is_S = bv.BitVector(size=len(x))
    assert len(is_S) == len(x)
    classify_SL(is_S, x)
    # mississippi$
    # LSLLSLLSLLLS
    # -*--*--*---*
    expected = [
        # -    *     -      -
        False, True, False, False,
        # *   -      -      *
        True, False, False, True,
        # -    -      -      *
        False, False, False, True
    ]
    assert len(is_S) == len(expected)
    for i, _ in enumerate(expected):
        assert is_LMS(is_S, i) == expected[i]


def test_base_case():
    assert sais("abc") == [0, 1, 2]
    assert sais("cba") == [2, 1, 0]
    assert sais("acb") == [0, 2, 1]


def test_mississippi():
    x = "mississippi"
    sa = sais(x)
    assert len(x) == len(sa)
    check_sorted(x, sa)


def test_sais_sorted():
    for _ in range(10):
        x = random_string(20, "abcd")  #random_string(1000)
        sa = sais(x)
        check_sorted(x, sa)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
