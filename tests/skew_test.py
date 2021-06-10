import typing as typ
from helpers import random_string, fibonacci_string
from pystr import skew_central, skew_terminal


def check(x: str, skew: typ.Callable[[str], list[int]]) -> None:
    sa0 = skew(x)
    assert len(sa0) == len(x) + 1
    assert list(sorted(sa0)) == list(range(len(x)+1))
    assert sa0[0] == len(x)


def test_skew_random() -> None:
    for _ in range(10):
        check(random_string(1000), skew_central.skew)
        check(random_string(1000), skew_terminal.skew)


def test_skew_fibonacci() -> None:
    for n in range(10, 15):
        check(fibonacci_string(n), skew_central.skew)
        check(fibonacci_string(n), skew_terminal.skew)


def test_skew_equal() -> None:
    for k in range(1, 20):
        check('a' * k, skew_central.skew)
        check('a' * k, skew_terminal.skew)
