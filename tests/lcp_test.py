"""Test lcp code."""

from helpers import fibonacci_string, random_string
from pystr.lcp import (compare_lcp, inverse_sa, lcp_from_sa,
                       sa_lcp_from_suffix_tree)
from pystr.sais import sais
from pystr.suffixtree import mccreight_st_construction


def check_lcp(x: str,
              sa: list[int],
              lcp: list[int]
              ) -> None:
    """Check lcp consistency."""
    assert len(sa) == len(x) + 1
    assert len(sa) == len(lcp)
    assert lcp[0] == 0            # first lcp is always zero
    for i in range(1, len(lcp)):
        assert lcp[i] == compare_lcp(x, sa[i], sa[i - 1])


def test_st_construction() -> None:
    """Test construction from suffix tree."""
    for _ in range(20):
        # smaller alpha for more branches...
        x = random_string(50, alpha="abc")

        # Including sentinel
        st = mccreight_st_construction(x)
        sa, lcp = sa_lcp_from_suffix_tree(st)
        assert sa == sais(x)
        check_lcp(x, sa, lcp)


def test_inverse() -> None:
    """Test inverse suffix array construction."""
    for _ in range(20):
        x = random_string(50, alpha="abc")
        sa = sais(x)
        isa = inverse_sa(sa)
        assert len(sa) == len(isa)
        assert set(sa) == set(isa)
        for i in range(len(sa)):
            assert sa[isa[i]] == i


def test_sa_construction() -> None:
    """Test construction from suffix array."""
    for _ in range(20):
        # smaller alpha for more branches...
        x = random_string(50, alpha="abc")
        sa = sais(x)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp)

    for n in range(10, 15):
        x = fibonacci_string(n)

        sa = sais(x)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
