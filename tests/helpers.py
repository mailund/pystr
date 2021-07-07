"""Helper functions for testing."""

import random
import string
from collections.abc import Iterable, Iterator, Callable
from pystr.subseq import SubSeq

# I'm not sure about the prototype here. I think I want
# to allow any number of paramters, if pytest can add
# mock objects and such... I haven't studied that sufficiently
# yet to have a good feeling for it.
# Underscored to prevent pytest from instantiating it.
_Test = Callable[..., None]


def collect_tests(tests: Iterable[tuple[str, _Test]]) -> type:
    """Wrap a list of tests into a class that contains them."""
    return type(
        '__generated_class__',
        (object,),
        {
            ('test_'+name): method
            for name, method in tests
        }
    )


def random_string(n: int, alpha: str = string.ascii_uppercase) -> str:
    """Create a random string."""
    return ''.join(random.choices(alpha, k=n))


def fibonacci_string(n: int) -> str:
    """Fibonacci string n; has length Fib(n+2)."""
    a, b = "a", "ab"
    for _ in range(n):
        a, b = b, a+b
    return b


def pick_random_patterns(x: str, n: int) -> Iterator[str]:
    """Pick a random pattern from a string."""
    for _ in range(n):
        i = random.randrange(0, len(x) - 1)
        j = random.randrange(i + 1, len(x))
        assert j > i  # Don't give us empty strings
        yield x[i:j]


def pick_random_patterns_len(x: str, n: int, patlen: int) -> Iterator[str]:
    """Pick a random pattern of a specifici length."""
    for _ in range(n):
        i = random.randrange(0, len(x) - 1)  # -1 because we don't want ""
        j = min(i + patlen, len(x))
        assert j > i  # Don't give us empty strings
        yield x[i:j]


def pick_random_prefix(x: str, n: int) -> Iterator[str]:
    """Pick a random prefix."""
    for _ in range(n):
        i = random.randrange(0, len(x))
        yield x[:i]


def pick_random_suffix(x: str, n: int) -> Iterator[str]:
    """Pick a random suffix."""
    for _ in range(n):
        i = random.randrange(0, len(x))
        yield x[i:]


def check_sorted(x: str, sa: list[int]) -> None:
    """Check that the suffixes in sa are sorted."""
    assert len(x) > 0
    assert len(x) == len(sa) or len(x) + 1 == len(sa)
    y = SubSeq[str](x)  # For faster comparison (faster than slicing)
    start = 0 if len(sa) == len(x) else 1  # skip sentinel if included
    for i in range(start, len(sa) - 1):
        j, k = sa[i], sa[i+1]
        assert y[j:] < y[k:], \
            f"String {x}, suffix x[{j}:] = {x[j:]} >= x[{k}:] = {x[k:]}"


def check_substring(x: str, p: str, i: int) -> bool:
    """Check that the substring x[i:i+len(p)] equals q."""
    return x[i:i+len(p)] == p


def check_matches(x: str, p: str, matches: Iterable[int]) -> None:
    """Check that the positions in matches contain p."""
    matches = list(matches)
    for i in matches:
        assert check_substring(x, p, i), \
            f"Substring {x[i:]} should match pattern {p}"


def check_equal_matches(x: str, p: str,
                        *algos: Callable[[str, str], Iterator[int]]) -> None:
    """Check that all algorithms give us the same matches."""
    # We sort the search results since some algorithms do not automatically
    # give us sorted output
    iters: list[list[int]] = [sorted(algo(x, p)) for algo in algos]
    print('Iters:', iters)
    for res in zip(*iters, strict=True):  # type: ignore
        assert all(res[i] == res[0] for i in range(1, len(res)))
