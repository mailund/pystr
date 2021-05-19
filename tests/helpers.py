import random
import string


def random_string(n: int) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=n))


def check_sorted(x: str, sa: list[int]):
    assert len(x) > 0 and len(x) == len(sa)
    for i in range(len(sa) - 1):
        j, k = sa[i], sa[i+1]
        assert x[j:] < x[k:], \
            f"String {x}, suffix x[{j}:] = {x[j:]} >= x[{k}:] = {x[k:]}"
