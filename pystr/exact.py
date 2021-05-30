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
from .output import colour                      # noqa: E402
from .output import indent, out                 # noqa: E402
from .cols import plain, yellow, green, red     # noqa: E402
from .cols import bright_green, bright_blue     # noqa: E402
from .cols import underline                     # noqa: E402


def naive_show_mismatch(x: str, p: str, i: int, j: int):
    out(indent(i), "i")
    out(colour(x)[i:i+j, green][i+j, red])
    out(indent(i), colour(p)[:j, green][j, red])
    out(indent(i+j), "j")
    out()


def naive_show_match(x: str, p: str, i: int):
    out(indent(i), "i")
    out(colour(x)[i:i+len(p), green])
    out(indent(i), green(p))
    out(indent(i+len(p)), "j")
    out()


def border_show_prefix_next_comp(x: str, p: str, i: int, b: int):
    out(indent(i), "i")
    out(colour(x)[i-b:i, green][i, yellow])
    out(indent(i - b), colour(p)[:b, green][b, yellow])
    out(indent(i), "b")
    out()


def kmp_show_prefix_next_comp(x: str, p: str, i: int, j: int):
    out(indent(i), "i")
    out(colour(x)[i-j:i, green][i, yellow])
    out(indent(i - j), colour(p)[:j, green][j, yellow])
    out(indent(i), "j")
    out()


def kmp_show_prefix_mismatch(x: str, p: str, i: int, j: int):
    out(indent(i), "i")
    out(colour(x)[i-j:i, green][i, red])
    out(indent(i - j), colour(p)[:j, green][j, red])
    out(indent(i), "j")
    out()


def bmh_next_comp(x: str, p: str, i: int):
    j = len(p)
    out(indent(i + j - 1), "v")
    out(colour(x)[i+j-1, yellow])
    out(indent(i), colour(p)[-1, yellow])
    out(indent(i + j - 1), "^")
    out()


def bmh_mismatch(x: str, p: str, i: int, j: int):
    col = red if x[i+j] != p[j] else green
    out(indent(i + j), "v")
    out(colour(x)[i+j, col][i+j+1:i+len(p), green])
    out(indent(i), colour(p)[j, col][j+1:, green])
    out(indent(i + j), "^")
    out()


def bmh_shift(x: str, p: str, i: int, j: int, shift: int):
    pos = i + len(p) - 1
    rmost = len(p) - shift - 1
    col = green if rmost >= 0 else red
    rmost_col = green if rmost >= 0 else plain
    out(indent(pos), "v")
    out(colour(x)[pos, col])
    out(indent(i + shift), colour(p)[rmost, rmost_col])
    out(indent(i + shift + rmost), "^")
    out()