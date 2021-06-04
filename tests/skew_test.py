from helpers import random_string, fibonacci_string, check_sorted
from pystr import skew


def check(x: str) -> None:
    sa = skew(x, include_sentinel=False)
    assert len(sa) == len(x)
    assert list(sorted(sa)) == list(range(len(x)))
    check_sorted(x, sa)

    sa0 = skew(x, include_sentinel=True)
    assert len(sa0) == len(x) + 1
    assert list(sorted(sa0)) == list(range(len(x)+1))
    assert sa0[0] == len(x)
    assert sa0[1:] == sa


def test_skew_random() -> None:
    for _ in range(10):
        check(random_string(1000))


def test_skew_fibonacci() -> None:
    for n in range(10, 15):
        check(fibonacci_string(n))


def test_skew_equal() -> None:
    for k in range(1, 20):
        check('a' * k)
