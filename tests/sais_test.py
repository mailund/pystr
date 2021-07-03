"""Test of sais algorithm."""

from pystr.sais import classify_sl, is_lms
from pystr.sais import sais
from pystr.bv import BitVector
from pystr.alphabet import Alphabet
from helpers import random_string, fibonacci_string, check_sorted


def test_remap() -> None:
    """Test that remapping works."""
    x = "mississippi"
    mapped, alpha = Alphabet.mapped_string_with_sentinel(x)
    assert mapped == bytearray([2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0])
    assert len(alpha) == 5

    for _ in range(10):
        x = random_string(1000)
        mapped, alpha = Alphabet.mapped_string_with_sentinel(x)
        assert set(mapped) == set(range(len(alpha)))


def test_classify() -> None:
    """Test that the SL classification works."""
    # mississippi$
    # LSLLSLLSLLLS
    x, _ = Alphabet.mapped_subseq_with_sentinel("mississippi")
    assert len(x) == len("mississippi") + 1

    is_s = BitVector(size=len(x))
    assert len(is_s) == len(x)

    classify_sl(is_s, x)

    expected = [
        # L    S     L      L      S     L      L
        False, True, False, False, True, False, False,
        # S   L      L      L      S
        True, False, False, False, True
    ]
    for i in range(len(is_s)):
        assert is_s[i] == expected[i]


def test_is_lms() -> None:
    """Test that is_lms works."""
    x, _ = Alphabet.mapped_subseq_with_sentinel("mississippi")
    assert len(x) == len("mississippi") + 1
    is_s = BitVector(len(x))
    assert len(is_s) == len(x)
    classify_sl(is_s, x)
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
    assert len(is_s) == len(expected)
    for i, _ in enumerate(expected):
        assert is_lms(is_s, i) == expected[i]

    for _ in range(10):
        z = random_string(20, "abcd")
        y, _ = Alphabet.mapped_subseq_with_sentinel(z)
        is_s = BitVector(len(y))
        classify_sl(is_s, y)

        assert is_s[len(y) - 1]
        assert is_lms(is_s, len(y) - 1)


def test_base_case() -> None:
    """Test that we can sort base cases."""
    assert sais("abc") == [3, 0, 1, 2]
    assert sais("cba") == [3, 2, 1, 0]
    assert sais("acb") == [3, 0, 2, 1]


def test_mississippi() -> None:
    """Test on mississippi."""
    x = "mississippi"
    sa = sais(x)
    assert len(x) == len(sa) - 1
    check_sorted(x, sa)


def test_sais_sorted() -> None:
    """Test that the sais suffix array is sorted."""
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
