from pystr.sais import classify_SL, is_LMS
from pystr.sais import sais
from pystr.bv import BitVector
from pystr.alphabet_string import String
from helpers import random_string, fibonacci_string, check_sorted


def test_remap() -> None:
    x = "mississippi"
    mapped = String(x)
    assert mapped == [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    assert len(mapped.alpha) == 5

    for _ in range(10):
        x = random_string(1000)
        mapped = String(x)
        assert set(mapped) == set(range(len(mapped.alpha)))


def test_classify() -> None:
    # mississippi$
    # LSLLSLLSLLLS
    x = String("mississippi")
    assert len(x) == len("mississippi") + 1

    is_S = BitVector(size=len(x))
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


def test_is_LMS() -> None:
    x = String("mississippi")
    assert len(x) == len("mississippi") + 1
    is_S = BitVector(len(x))
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

    for _ in range(10):
        z = random_string(20, "abcd")
        y = String(z)
        is_S = BitVector(len(y))
        classify_SL(is_S, y)

        assert is_S[len(y) - 1]
        assert is_LMS(is_S, len(y) - 1)


def test_base_case() -> None:
    assert sais("abc") == [3, 0, 1, 2]
    assert sais("cba") == [3, 2, 1, 0]
    assert sais("acb") == [3, 0, 2, 1]


def test_mississippi() -> None:
    x = "mississippi"
    sa = sais(x)
    assert len(x) == len(sa) - 1
    check_sorted(x, sa)


def test_adccacacbbccdccdbccb() -> None:
    x = "adccacacbbccdccdbccb"
    sa = sais(x)
    assert len(x) == len(sa) - 1
    assert sa[0] == len(x)
    check_sorted(x, sa)


def test_sais_sorted() -> None:
    for _ in range(10):
        x = random_string(1000)
        sa = sais(x)
        check_sorted(x, sa)

    for n in range(10, 15):
        x = fibonacci_string(n)
        sa = sais(x)
        check_sorted(x, sa)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
