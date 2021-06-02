from helpers import random_string, fibonacci_string, check_sorted
from pystr import skew


def test_skew_sorted():
    for k in range(10):
        x = random_string(1000)
        sa = skew(x, include_sentinel=False)
        check_sorted(x, sa)
        sa0 = skew(x, include_sentinel=True)
        assert sa0[0] == len(x)
        assert sa0[1:] == sa

    for n in range(10, 15):
        x = fibonacci_string(n)
        sa = skew(x, include_sentinel=False)
        check_sorted(x, sa)
        sa0 = skew(x, include_sentinel=True)
        assert sa0[0] == len(x)
        assert sa0[1:] == sa
