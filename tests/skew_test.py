import testsetup
from helpers import random_string, check_sorted
from skew import skew


def test_skew_sorted():
    for k in range(10):
        x = random_string(10)
        sa = skew(x)
        check_sorted(x, sa)
