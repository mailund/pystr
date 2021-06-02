from helpers import random_string, fibonacci_string
from pystr import mccreight_st_construction, sais
from pystr.lcp import compare_lcp, sa_lcp_from_suffix_tree
from pystr.lcp import inverse_sa, lcp_from_sa


def check_lcp(x: str, sa: list[int], lcp: list[int], include_sentinel: bool):
    assert len(sa) == len(x) + include_sentinel
    assert len(sa) == len(lcp)
    assert lcp[0] == 0            # first lcp is always zero
    for i in range(1, len(lcp)):
        assert lcp[i] == compare_lcp(x, sa[i], sa[i-1])


def test_st_construction():
    for _ in range(20):
        # smaller alpha for more branches...
        x = random_string(50, alpha="abc")

        # Including sentinel
        st = mccreight_st_construction(x, include_sentinel=True)
        sa, lcp = sa_lcp_from_suffix_tree(st)
        assert sa == sais(x)
        check_lcp(x, sa, lcp, include_sentinel=True)

        # Excluding sentinel
        st = mccreight_st_construction(x, include_sentinel=False)
        sa, lcp = sa_lcp_from_suffix_tree(st)
        assert sa == sais(x)[1:]
        check_lcp(x, sa, lcp, include_sentinel=False)


def test_inverse():
    for _ in range(20):
        x = random_string(50, alpha="abc")
        sa = sais(x)
        isa = inverse_sa(sa)
        assert len(sa) == len(isa)
        assert set(sa) == set(isa)
        for i in range(len(sa)):
            assert sa[isa[i]] == i


def test_sa_construction():
    for _ in range(20):
        # smaller alpha for more branches...
        x = random_string(50, alpha="abc")
        sa = sais(x, include_sentinel=True)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp, include_sentinel=True)

        sa = sais(x, include_sentinel=False)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp, include_sentinel=False)

    for n in range(10, 15):
        x = fibonacci_string(n)

        sa = sais(x, include_sentinel=True)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp, include_sentinel=True)

        sa = sais(x, include_sentinel=False)
        lcp = lcp_from_sa(x, sa)
        check_lcp(x, sa, lcp, include_sentinel=False)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
