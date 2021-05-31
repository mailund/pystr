import _setup  # noqa: F401

from pystr import mccreight_st_construction, sais
from pystr.lcp import sa_lcp_from_suffix_tree


def compare_lcp(x: str, y: str) -> int:
    m = min(len(x), len(y))
    for i in range(m):
        if x[i] != y[i]:
            return i
    else:
        return m


def check_lcp(x: str, sa: list[int], lcp: list[int]):
    assert len(sa) == len(x) + 1  # we include sentinel
    assert len(sa) == len(lcp)
    assert lcp[0] == 0            # first lcp is always zero

    for i in range(1, len(lcp)):
        assert lcp[i] == compare_lcp(x[sa[i]:], x[sa[i-1]:])


def test_st_construction():
    x = "aabca"
    st = mccreight_st_construction(x, include_sentinel=True)
    sa, lcp = sa_lcp_from_suffix_tree(st)
    assert sa == sais(x)
    check_lcp(x, sa, lcp)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
