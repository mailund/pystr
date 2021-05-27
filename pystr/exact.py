# Simple exact matching algorithms
from typing import Iterator
from collections import defaultdict
from .border_array import strict_border_array


def naive(x: str, p: str,
          progress=False,
          interactive=False,
          ) -> Iterator[int]:
    # If we have an empty string, j is never set,
    # and that can mess up the progress text. So we
    # need to give it a value here, just for that special case.
    j = 0
    for i in range(len(x) - len(p) + 1):
        if progress:
            print(bright_green(f"Iteration {i}"))

        for j in range(len(p)):
            if x[i + j] != p[j]:
                break
        else:
            # We made it through without breaking...
            yield i

        if progress:
            if j == len(p) - 1 and x[i + j] == p[j]:
                naive_show_match(x, p, i)
                print(bright_green(f"We matched at index {i}"))
            else:
                naive_show_mismatch(x, p, i, j)

        if interactive:  # pragma: no cover
            input("Press ENTER to continue")


def border(x: str, p: str,
           progress=False,
           interactive=False
           ) -> Iterator[int]:
    assert p, "Doesn't handle empty patterns"

    # Build the border array
    ba = strict_border_array(p)

    # Now search...
    b = 0
    for i in range(len(x)):
        if progress:
            print(bright_blue(f"Iteration {i}"))
            border_show_prefix_next_comp(x, p, i, b)

        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        if progress:
            border_show_prefix_next_comp(x, p, i + 1, b)
            if b == len(p):
                print(bright_green(f"We matched at index {i - len(p)}"))
                print()

        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]

        if interactive:  # pragma: no cover
            input("Press ENTER to continue")


def kmp(x: str, p: str,
        progress=False,
        interactive=False
        ) -> Iterator[int]:

    ba = strict_border_array(p)
    i, j = 0, 0
    while i < len(x):

        if progress:
            kmp_show_prefix_next_comp(x, p, i, j)

        while j < len(p) and i < len(x):
            if x[i] != p[j]:
                break
            i += 1
            j += 1

        if j == len(p):
            yield i - len(p)

        if progress:
            kmp_show_prefix_mismatch(x, p, i, j)
            if j == len(p):
                print(bright_green(f"We matched at index {i - len(p)}"))
                print()

        if j == 0:
            i += 1
        else:
            j = ba[j - 1]

        if interactive:  # pragma: no cover
            input("Press ENTER to continue")


def bmh(x: str, p: str,
        progress=False,
        interactive=False
        ) -> Iterator[int]:

    jump: dict[str, int] = \
        defaultdict(lambda: len(p))
    for j in range(len(p) - 1):  # skip last index!
        jump[p[j]] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:

        if progress:
            print(bright_blue(f"Attempting at index {i}"))
            bmh_next_comp(x, p, i)

        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        if progress:
            print(underline("Matching characters:"))
            bmh_mismatch(x, p, i, j)
            if j == 0 and p[0] == x[i]:
                print(bright_green(f"We matched at index {i}\n"))
            print(underline("Shifting:"))
            bmh_shift(x, p, i, j, jump[x[i + len(p) - 1]])
            if interactive:  # pragma: no cover
                input("Press ENTER to continue")

        i += jump[x[i + len(p) - 1]]


# Code for visualising the algorithms...
from .output import clamp                    # noqa: E402
from .cols import yellow, green, red         # noqa: E402
from .cols import bright_green, bright_blue  # noqa: E402
from .cols import underline                  # noqa: E402


def naive_show_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i]}{green(cx[i:i+j])}{red(cx[i+j])}{cx[i+j+1:]}")
    print(f"{' ' * i}{green(cp[:j])}{red(cp[j])}{cp[j+1:]}")
    print(f"{' ' * (i + j)}j")
    print()


def naive_show_match(x: str, p: str, i: int):
    cx = clamp(x)
    print(f"{' ' * i}i")
    print(f"{cx[:i]}{green(cx[i:i+len(p)])}{cx[i+len(p):]}")
    print(f"{' ' * i}{green(p)}")
    print(f"{' ' * (i + len(p))}j")
    print()


def border_show_prefix_next_comp(x: str, p: str, i: int, b: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-b]}{green(cx[i-b:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - b)}{green(cp[:b])}{yellow(cp[b])}{cp[b+1:]}")
    print(f"{' ' * i}b")
    print()


def kmp_show_prefix_next_comp(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{yellow(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()


def kmp_show_prefix_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{red(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{red(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()


def bmh_next_comp(x: str, p: str, i: int):
    cx = clamp(x)
    j = len(p)
    print(f"{' ' * (i + j - 1)}v")
    print(f"{cx[:i+j-1]}{yellow(cx[i+j-1])}{cx[i+j:]}")
    print(f"{' ' * i}{p[:-1]}{yellow(p[-1])}")
    print(f"{' ' * (i + j - 1)}^")
    print()


def bmh_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    col = red if x[i+j] != p[j] else green
    print(f"{' ' * (i + j)}v")
    print(f"{cx[:i+j]}{col(cx[i+j])}{green(cx[i+j+1:i+len(p)])}{cx[i+len(p):]}")  # noqa: E501
    print(f"{' ' * i}{cp[:j]}{col(cp[j])}{green(cp[j+1:])}")
    print(f"{' ' * (i + j)}^")
    print()


def bmh_shift(x: str, p: str, i: int, j: int, shift: int):
    cx = clamp(x)
    cp = clamp(p)
    pos = i + len(p) - 1
    rmost = len(p) - shift - 1
    col = green if rmost >= 0 else red
    print(f"{' ' * (pos)}v")
    print(f"{cx[:pos]}{col(cx[pos])}{cx[pos+1:]}")  # noqa: E501
    print(f"{' ' * (i + shift)}{cp[:rmost]}{green(cp[rmost])}{cp[rmost+1:]}")  # noqa: E501
    print(f"{' ' * (i + shift + rmost)}^")
    print()
