# Simple exact matching algorithms
import argparse
from collections import defaultdict
from pystr.border_array import strict_border_array


def hit_enter(interactive: bool):
    if interactive:
        input("Press ENTER to continue")


def naive(x: str, p: str, interactive: bool) -> None:
    # If we have an empty string, j is never set,
    # and that can mess up the progress text. So we
    # need to give it a value here, just for that special case.
    j = 0
    for i in range(len(x) - len(p) + 1):
        print(bright_green(f"Iteration {i}"))

        for j in range(len(p)):
            if x[i + j] != p[j]:
                break
        else:
            # We made it through without breaking...
            pass  # yield

        if j == len(p) - 1 and x[i + j] == p[j]:
            naive_show_match(x, p, i)
            print(bright_green(f"We matched at index {i}"))
        else:
            naive_show_mismatch(x, p, i, j)

        hit_enter(interactive)


def border(x: str, p: str, interactive: bool) -> None:
    assert p, "Doesn't handle empty patterns"

    # Build the border array
    ba = strict_border_array(p)

    # Now search...
    b = 0
    for i in range(len(x)):
        print(bright_blue(f"Iteration {i}"))
        border_show_prefix_next_comp(x, p, i, b)

        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        border_show_prefix_next_comp(x, p, i + 1, b)
        if b == len(p):
            print(bright_green(f"We matched at index {i - len(p)}"))
            print()

        if b == len(p):
            # yield i - len(p) + 1
            b = ba[b - 1]

        hit_enter(interactive)


def kmp(x: str, p: str, interactive: bool) -> None:

    ba = strict_border_array(p)
    i, j = 0, 0
    while i < len(x):

        kmp_show_prefix_next_comp(x, p, i, j)

        while j < len(p) and i < len(x):
            if x[i] != p[j]:
                break
            i += 1
            j += 1

        # if j == len(p):
        #     yield i - len(p)

        kmp_show_prefix_mismatch(x, p, i, j)
        if j == len(p):
            print(bright_green(f"We matched at index {i - len(p)}"))
            print()

        if j == 0:
            i += 1
        else:
            j = ba[j - 1]

        hit_enter(interactive)


def bmh(x: str, p: str, interactive) -> None:

    jump: dict[str, int] = \
        defaultdict(lambda: len(p))
    for j in range(len(p) - 1):  # skip last index!
        jump[p[j]] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:

        print(bright_blue(f"Attempting at index {i}"))
        bmh_next_comp(x, p, i)

        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            pass  # yield i

        print(underline("Matching characters:"))
        bmh_mismatch(x, p, i, j)
        if j == 0 and p[0] == x[i]:
            print(bright_green(f"We matched at index {i}\n"))
        print(underline("Shifting:"))
        bmh_shift(x, p, i, j, jump[x[i + len(p) - 1]])
        hit_enter(interactive)

        i += jump[x[i + len(p) - 1]]


# Code for visualising the algorithms...
from pystr_vis import colour                             # noqa: E402
from pystr_vis import indent                             # noqa: E402
from pystr_vis.cols import plain, yellow, green, red     # noqa: E402
from pystr_vis.cols import bright_green, bright_blue     # noqa: E402
from pystr_vis.cols import underline                     # noqa: E402


def naive_show_mismatch(x: str, p: str, i: int, j: int):
    print(indent(i), "i", sep="")
    print(colour(x)[i:i+j, green][i+j, red], sep="")
    print(indent(i), colour(p)[:j, green][j, red], sep="")
    print(indent(i+j), "j", sep="")
    print()


def naive_show_match(x: str, p: str, i: int):
    print(indent(i), "i", sep="")
    print(colour(x)[i:i+len(p), green], sep="")
    print(indent(i), green(p), sep="")
    print(indent(i+len(p)), "j", sep="")
    print()


def border_show_prefix_next_comp(x: str, p: str, i: int, b: int):
    print(indent(i), "i", sep="")
    print(colour(x)[i-b:i, green][i, yellow], sep="")
    print(indent(i - b), colour(p)[:b, green][b, yellow], sep="")
    print(indent(i), "b", sep="")
    print()


def kmp_show_prefix_next_comp(x: str, p: str, i: int, j: int):
    print(indent(i), "i", sep="")
    print(colour(x)[i-j:i, green][i, yellow], sep="")
    print(indent(i - j), colour(p)[:j, green][j, yellow], sep="")
    print(indent(i), "j", sep="")
    print()


def kmp_show_prefix_mismatch(x: str, p: str, i: int, j: int):
    print(indent(i), "i", sep="")
    print(colour(x)[i-j:i, green][i, red], sep="")
    print(indent(i - j), colour(p)[:j, green][j, red], sep="")
    print(indent(i), "j", sep="")
    print()


def bmh_next_comp(x: str, p: str, i: int):
    j = len(p)
    print(indent(i + j - 1), "v", sep="")
    print(colour(x)[i+j-1, yellow], sep="")
    print(indent(i), colour(p)[-1, yellow], sep="")
    print(indent(i + j - 1), "^", sep="")
    print()


def bmh_mismatch(x: str, p: str, i: int, j: int):
    col = red if x[i+j] != p[j] else green
    print(indent(i + j), "v", sep="")
    print(colour(x)[i+j, col][i+j+1:i+len(p), green], sep="")
    print(indent(i), colour(p)[j, col][j+1:, green], sep="")
    print(indent(i + j), "^", sep="")
    print()


def bmh_shift(x: str, p: str, i: int, j: int, shift: int):
    pos = i + len(p) - 1
    rmost = len(p) - shift - 1
    col = green if rmost >= 0 else red
    rmost_col = green if rmost >= 0 else plain
    print(indent(pos), "v", sep="")
    print(colour(x)[pos, col], sep="")
    print(indent(i + shift), colour(p)[rmost, rmost_col], sep="")
    print(indent(i + shift + rmost), "^", sep="")
    print()


def main():
    algos = {
        'naive': naive,
        'border': border,
        'kmp': kmp,
        'bmh': bmh,
    }
    parser = argparse.ArgumentParser(
        description='Display run of a classic exact pattern matching algorithm.')  # noqa: E501

    parser.add_argument('-i', '--interactive',
                        dest='interactive', action='store_true',
                        help='the visualisation should pause between steps (default).')  # noqa: E501
    parser.add_argument('-n', '--not-interactive',
                        dest='interactive', action='store_false',
                        help='the visualisation should not pause between steps.')        # noqa: E501
    parser.set_defaults(interactive=True)

    parser.add_argument('algo', choices=algos.keys(),
                        help='algorithm to run')
    parser.add_argument('x', metavar='x', type=str,
                        help='string to search in.')
    parser.add_argument('p', metavar='p', type=str,
                        help='string to search for.')

    args = parser.parse_args()
    algos[args.algo](args.x, args.p, args.interactive)
