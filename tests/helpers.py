import random
import string
from collections.abc import Iterator


def random_string(n: int) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=n))


def check_sorted(x: str, sa: list[int]):
    assert len(x) > 0 and len(x) == len(sa)
    # FIXME: Use smarter slices here...
    for i in range(len(sa) - 1):
        j, k = sa[i], sa[i+1]
        assert x[j:] < x[k:], \
            f"String {x}, suffix x[{j}:] = {x[j:]} >= x[{k}:] = {x[k:]}"


def check_substring(x: str, p: str, i: int) -> bool:
    return x[i:i+len(p)] == p


def check_matches(x: str, p: str, matches: Iterator[int]):
    for i in matches:
        assert check_substring(x, p, i), \
            f"Substring {x[i:]} should match pattern {p}"
