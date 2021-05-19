import testsetup
from helpers import random_string, check_sorted
from suffixtree import naive_st_construction, mccreight_st_construction


def test_naive_sorted():
    for k in range(10):
        x = random_string(10)
        st = naive_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator


def test_mccreight_sorted():
    for k in range(10):
        x = random_string(10)
        st = mccreight_st_construction(x)
        check_sorted(x, list(st.root))  # using the leaf iterator
