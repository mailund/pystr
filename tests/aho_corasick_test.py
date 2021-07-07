"""Test Aho-Corasick."""

from helpers import fibonacci_string, pick_random_patterns, random_string
from pystr.aho_corasick import aho_corasick
from pystr.exact import naive


def test_abc() -> None:
    """Do basic tests."""
    x = "abcabcab"
    p = ("abc", "a", "b", "")
    for label, i in aho_corasick(x, *p):
        assert x[i:].startswith(p[label])


def compare_naive(x: str, pats: list[str]) -> bool:
    """Compare with naive exact matching."""
    naive_res: list[tuple[int, int]] = []
    for i, p in enumerate(pats):
        naive_res.extend((i, j) for j in naive(x, p))
    naive_res.sort()

    ac_res = list(aho_corasick(x, *pats))
    ac_res.sort()

    return naive_res == ac_res


def test_compare_naive() -> None:
    """Compare with naive exact matching."""
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        # need to go through set to remove duplicates.
        # naive can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with naive:\nx="{x}"\nps={pats}\n\n')
        assert compare_naive(x, pats)
    for _ in range(10):
        x = random_string(100)  # try larger alphabet
        # need to go through set to remove duplicates.
        # naive can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with naive:\nx="{x}"\nps={pats}\n\n')
        assert compare_naive(x, pats)

    for n in range(10, 15):
        x = fibonacci_string(n)
        # need to go through set to remove duplicates.
        # naive can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with naive:\nx="{x}"\nps={pats}\n\n')
        assert compare_naive(x, pats)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
