import argparse
from typing import Callable, Sequence

from pystr.skew import bucket_sort, u_idx, safe_idx, \
    SkewTriplet, SkewTripletDict, triplet

from pystr_vis import colour, Table, ColSpec, L, R, Align
from pystr_vis.cols import Colour, \
    strip_ansi, ansifree_len, \
    underline, bright_yellow, \
    bright_cyan, bright_blue, bright_green, \
    red, green, blue, magenta, cyan, yellow

INTERACTIVE = True
TERMINAL_SENTINEL = 0
TERMINAL_SENTINEL_SYMBOL = '$'
CENTRAL_SENTINEL = 1
CENTRAL_SENTINEL_SYMBOL = '#'

BLOCK_COLS = [green, yellow, cyan, magenta, bright_blue]

Alpha = dict[int, str]


def hit_enter() -> None:
    if INTERACTIVE:
        input("Press ENTER to continue")


# SECTION Helpers for displaying integer strings


def remap_str(x: str) -> tuple[list[int], Alpha]:
    str2int: dict[str, int] = {}
    int2str: dict[int, str] = {}
    k = 2
    for a in sorted(set(x)):
        str2int[a] = k
        int2str[k] = a
        k += 1

    mapped_str = [str2int[a] for a in x]
    return mapped_str, int2str


def map_char(a: int, alpha: Alpha, width: int) -> str:
    if a == TERMINAL_SENTINEL:
        return TERMINAL_SENTINEL_SYMBOL if width == 1 \
            else f"<{TERMINAL_SENTINEL_SYMBOL*width}>"
    if a == CENTRAL_SENTINEL:
        return CENTRAL_SENTINEL_SYMBOL if width == 1 \
            else f"<{CENTRAL_SENTINEL_SYMBOL*width}>"
    s = strip_ansi(alpha[a])
    return s if len(s) == 1 else f"[{s}]"


Colourer = Callable[[int, int, str, Sequence[int]], str]
Transformer = Callable[[Sequence[int]], Sequence[int]]


def default_colour(i: int, a: int, mapped_a: str, x: Sequence[int]) -> str:
    # Colours sentinels and nothing else
    sentinel_cols = [blue, red]
    if a <= 1:
        return sentinel_cols[a](mapped_a)
    else:
        return mapped_a


def map_str(x: Sequence[int],
            alpha: Alpha,
            col: Colourer = default_colour
            ) -> str:
    # assuming here that all characters in alpha have the same with...
    a, *_ = alpha.values()
    width = ansifree_len(a)
    return ''.join(
        col(i, a, map_char(a, alpha, width), x) for i, a in enumerate(x)
    )

# !SECTION

# SECTION The Skew algorithm

# I use variants of these for the visualisation to show the central
# and terminal sentinels as different


def collect_alphabet(x: list[int], idx: list[int]) -> SkewTripletDict:
    "Map the triplets starting at idx to a new alphabet."
    # In the show version, add two sentinel characters. (Doesn't
    # matter what they are, we just need their size...)
    alpha: SkewTripletDict = {
        # These triplets don't exist, but they represent the
        # two sentinels. We never look them up, so they are only
        # here to give us the right alphabet size
        (0, 0, 0): 0,
        (-1, -1, -1): 1
    }
    for i in idx:
        trip = triplet(x, i)
        if trip not in alpha:
            alpha[trip] = len(alpha)
    return alpha


def build_u(x: list[int], alpha: SkewTripletDict) -> list[int]:
    "Construct u string, using 1 as central sentinel."
    # By putting the i % 3 == 1 indices first, we know that the central
    # sentinel will always be at len(u) // 2.
    return [*(alpha[triplet(x, i)] for i in range(1, len(x), 3)),
            CENTRAL_SENTINEL,
            *(alpha[triplet(x, i)] for i in range(2, len(x), 3))]


def default_suffix_transform(x: Sequence[int]) -> Sequence[int]:
    return x  # let's you modify x before colour


def sa_table(name: str,
             saXX: list[int],
             x: list[int],
             alpha: Alpha,
             tr: Transformer = default_suffix_transform,
             col: Colourer = default_colour) \
        -> Table:
    tbl = Table(
        ColSpec("sa", align=Align.RIGHT),
        ColSpec("idx", align=Align.RIGHT),
        ColSpec("suf", align=Align.LEFT)
    )
    for i, j in enumerate(saXX):
        row = tbl.add_row()
        row["sa"] = f"{name}[{i:>2}] ="
        row["idx"] = str(j)
        row["suf"] = map_str(tr(x[j:]), alpha, col)
    return tbl


def highlight_offset(offset: int) -> Colourer:
    def col(i: int, a: int, a_mapped: str, x: Sequence[int]) -> str:
        if i == offset:
            return bright_yellow(a_mapped)
        else:
            return default_colour(i, a, a_mapped, x)
    return col


def pad_3(x: Sequence[int]) -> Sequence[int]:
    return tuple(x) + (TERMINAL_SENTINEL,) * max(0, 3 - len(x))


def show_radix_sort(x: list[int],
                    alpha: Alpha,
                    SA12: list[int]
                    ) -> list[int]:
    # This is handled in the actual algorithm, but we
    # get it from alpha in the visualisation
    asize = len(alpha) + 2  # +2 for sentinels

    for offset in [2, 1, 0]:
        print(underline(f"Bucket sorting with offset {offset}:\n"))
        SA12 = bucket_sort(x, asize, SA12, offset)
        tbl = sa_table("SA12", SA12, x, alpha, pad_3, highlight_offset(offset))
        print(tbl)
        print()
        hit_enter()
    return SA12


def show_sorted_SA12(x: list[int],
                     alpha: Alpha,
                     SA12: list[int],
                     umap: dict[SkewTriplet, int],
                     blocked: bool = False
                     ) -> Table:
    # This is handled in the actual algorithm, but we
    # get it from alpha in the visualisation
    if blocked:
        cols = BLOCK_COLS
    else:
        cols = [green]

    def col(i: int, a: int, a_mapped: str, x: Sequence[int]) -> str:
        if i < 3:
            idx = umap[triplet(x, 0)] - 2
            return cols[idx % len(cols)](a_mapped)
        else:
            return default_colour(i, a, a_mapped, x)

    return sa_table("SA12", SA12, x, alpha, col=col)


def col_block(i: int, a: int, a_mapped: str, x: Sequence[int]) -> str:
    if a < 2:
        # handle sentinels as usual.
        return default_colour(i, a, a_mapped, x)
    idx = a - 2
    return BLOCK_COLS[idx % len(BLOCK_COLS)](a_mapped)


def col_notsent(col: Colour) -> Colourer:
    def colour_a(i: int, a: int, a_mapped: str, x: Sequence[int]) -> str:
        if a < 2:
            # handle sentinels as usual.
            return default_colour(i, a, a_mapped, x)
        else:
            return col(a_mapped)
    return colour_a


def merge_show_arrays(x: list[int],
                      SA12: list[int], SA3: list[int], SA: list[int],
                      alpha: Alpha,
                      merge_index_i: int, merge_index_j: int
                      ) -> Table:
    m = max(len(SA12), len(SA3), len(SA))
    tbl = Table(
        ColSpec("sa12_ptr"), ColSpec("sa12"), ColSpec("sa12_suf"),
        ColSpec("sa3_ptr"), ColSpec("sa3"), ColSpec("sa3_suf"),
        ColSpec("sa"), ColSpec("sa_suf")
    )
    for _ in range(m):
        tbl.add_row()
    for i, j in enumerate(SA12):
        tbl[i]["sa12"] = f"SA12[{i:>2}] = {SA12[i]:>2} ="
        tbl[i]["sa12_suf"] = map_str(x[j:], alpha)
    for i, j in enumerate(SA3):
        tbl[i]["sa3"] = f"SA3[{i:>2}] = {SA3[i]:>2}"
        tbl[i]["sa3_suf"] = map_str(x[j:], alpha)
    for i, j in enumerate(SA):
        tbl[i]["sa"] = green(f"SA[{i:>2}] = {SA[i]:>2} =")
        tbl[i]["sa_suf"] = green(map_str(x[j:], alpha))

    for i in range(merge_index_i):
        tbl[i]["sa12"] = red(strip_ansi(tbl[i]["sa12"]))
        tbl[i]["sa12_suf"] = red(strip_ansi(tbl[i]["sa12_suf"]))

    for i in range(merge_index_j):
        tbl[i]["sa3"] = red(strip_ansi(tbl[i]["sa3"]))
        tbl[i]["sa3_suf"] = red(strip_ansi(tbl[i]["sa3_suf"]))

    tbl[merge_index_i]["sa12_ptr"] = "i ->"
    tbl[merge_index_i]["sa12"] = yellow(strip_ansi(tbl[merge_index_i]["sa12"]))
    tbl[merge_index_i]["sa12_suf"] = yellow(
        strip_ansi(tbl[merge_index_i]["sa12_suf"]))
    tbl[merge_index_j]["sa3_ptr"] = "j ->"
    tbl[merge_index_j]["sa3"] = yellow(strip_ansi(tbl[merge_index_j]["sa3"]))
    tbl[merge_index_j]["sa3_suf"] = yellow(
        strip_ansi(tbl[merge_index_j]["sa3_suf"]))

    return tbl


def show_less(ii: int, jj: int,
              x: list[int], SA12: list[int], SA3: list[int],
              ISA: dict[int, int], alpha: Alpha) -> bool:

    print(underline("Comparing:\n"))
    print('\t', map_str(x[ii:], alpha))
    print('\t', map_str(x[jj:], alpha))
    print()
    print(f"with {ii} mod 3 = {ii%3} and {jj} mod 3 = {jj%3}")
    print()

    # This is a mighty ugly hack to get the width of a character,
    # but for something like this, I don't really care
    w = ansifree_len(next(iter(alpha.values())))

    a = safe_idx(x, ii)
    b = safe_idx(x, jj)
    if a < b:
        print(f"'{map_char(a, alpha, w)}' < '{map_char(b, alpha, w)}' => True")  # noqa: E501
        hit_enter()
        return True
    if a > b:
        print(f"'{map_char(a, alpha, w)}' > '{map_char(b, alpha, w)}' => False")  # noqa: E501
        hit_enter()
        return False

    if ii % 3 != 0 and jj % 3 != 0:
        if ISA[ii] < ISA[jj]:
            print(f"ISA[{ii}] < ISA[{jj}] => True")
            return True
        else:
            print(f"ISA[{ii}] > ISA[{jj}] => False")
            return False

    print("We cannot determine the order from the first characters or ISA,")
    print("so we have to compare one index further along.")
    print(f"i: {ii} -> {ii+1}, j: {jj} -> {jj+1}.")
    print()
    return show_less(ii+1, jj+1, x, SA12, SA3, ISA, alpha)


def show_merge(x: list[int],
               SA12: list[int], SA3: list[int],
               alpha: Alpha) -> list[int]:
    print(bright_cyan(underline("\n\nMerging lists\n\n")))

    ISA = {SA12[i]: i for i in range(len(SA12))}

    i, j = 0, 0
    SA: list[int] = []
    while i < len(SA12) and j < len(SA3):
        print(underline("\nLists to merge:\n"))
        print(merge_show_arrays(x, SA12, SA3, SA, alpha, i, j))
        print()

        print(f"We must compare SA12[{i}] = {SA12[i]} " +
              f"against SA3[{j}] = {SA3[j]}.")
        print()
        print(
            Table(R, L).
            append_row("", f"i = {SA12[i]}").
            append_row("", "v").
            append_row(f"SA12[{i}] =", map_str(x[SA12[i]:], alpha)).
            append_row(f"SA3[{j}] =", map_str(x[SA3[j]:], alpha)).
            append_row("", "^").
            append_row("", f"j = {SA3[j]}")
        )
        print()

        if show_less(SA12[i], SA3[j], x, SA12, SA3, ISA, alpha):
            SA.append(SA12[i])
            i += 1
        else:
            SA.append(SA3[j])
            j += 1

    print()
    print(underline("Done merging, so appending the remaining list"))
    SA.extend(SA12[i:])
    SA.extend(SA3[j:])
    return SA


def skew_rec(x: list[int], alpha: Alpha) -> list[int]:
    "Recursive skew SA construction algorithm."

    # This is handled in the actual algorithm, but we
    # get it from alpha in the visualisation
    asize = len(alpha) + 2  # +2 for sentinels

    print(colour("Sorting SA12 indices...")[:, bright_cyan & underline])
    print(underline("SA12 indices:\n"))
    SA12 = [i for i in range(len(x)) if i % 3 != 0]
    tbl = sa_table("SA12", SA12, x, alpha)
    print(tbl)
    print()
    hit_enter()
    print()

    SA12 = show_radix_sort(x, alpha, SA12)
    skew_new_alpha = collect_alphabet(x, SA12)

    print(underline("Triplets sorted:\n"))
    print(show_sorted_SA12(x, alpha, SA12, skew_new_alpha, False))
    print()
    hit_enter()
    print()

    print(colour("\nDivide and conquer...\n")[:, bright_cyan & underline])
    print(underline("Examining triplets:\n"))
    print(show_sorted_SA12(x, alpha, SA12, skew_new_alpha, True))
    print()
    hit_enter()
    print()

    skew_new_alpha = collect_alphabet(x, SA12)
    if len(skew_new_alpha) - 2 == len(SA12):  # -2 for $ and #
        print(underline(bright_green(
            "All triplets are unique, so we don't need to recurse.\n")))

    if len(skew_new_alpha) - 2 < len(SA12):
        print(underline("We have duplicated triplets and must recurse.\n"))

        # Make my kind of alpha for the visualisation
        new_alpha: dict[int, str] = {}
        for trip, a in skew_new_alpha.items():
            if a < 2:
                continue  # skip sentinels
            new_alpha[a] = map_str(trip, alpha)

        print('Numbering:')
        print(blue(f"{TERMINAL_SENTINEL_SYMBOL:>3}"), '=>', 0)
        print(red(f"{CENTRAL_SENTINEL_SYMBOL:>3}"), '=>', 1)
        for i, (a, s) in enumerate(new_alpha.items()):
            print(BLOCK_COLS[i % len(BLOCK_COLS)](strip_ansi(s)), '=>', a)

        u = build_u(x, skew_new_alpha)  # FIXME: insert central sentinel

        print()
        print(
            Table(R, L, L).
            append_row(f"x[1:]{red(CENTRAL_SENTINEL_SYMBOL)}x[2:]",
                       "=",
                       map_str(x[1:], alpha) +
                       red(CENTRAL_SENTINEL_SYMBOL) +
                       map_str(x[2:], alpha)).
            append_row("u",
                       "=",
                       map_str(u, new_alpha, col=col_block)).
            append_row("", "=",
                       "["+', '.join(col_block(i, a, str(a), u)
                                     for i, a in enumerate(u)) + "]"
                       )
        )

        print()
        hit_enter()
        print()

        sa_u = skew_rec(u, new_alpha)
        m = len(sa_u) // 2
        SA12 = [u_idx(i, m) for i in sa_u if i != m]

        print(colour("\nBack from the recursion\n")
              [:, underline & bright_cyan])
        print(underline("SA12 are now sorted:\n"))
        print(sa_table("SA12", SA12, x, alpha, col=col_notsent(green)))
        print()
        hit_enter()
        print()

    print(underline("Extracting SA3 based on SA1.\n"))
    SA3 = ([len(x) - 1] if len(x) % 3 == 1 else []) + \
        [i - 1 for i in SA12 if i % 3 == 1]
    print(sa_table("SA3", SA3, x, alpha, pad_3, highlight_offset(1)))
    print()
    hit_enter()

    print(underline("Bucket sort SA3.\n"))
    SA3 = bucket_sort(x, asize, SA3)
    print(sa_table("SA3", SA3, x, alpha, pad_3, highlight_offset(0)))
    print()
    hit_enter()

    SA = show_merge(x, SA12, SA3, alpha)

    print(bright_green(underline("\n\nSuffix array sorted.\n")))
    print(sa_table("SA", SA, x, alpha, col=col_notsent(green)))
    print()
    hit_enter()

    return SA


# !SECTION

# SECTION Main application


def show_skew() -> None:
    global INTERACTIVE, TERMINAL_SENTINEL_SYMBOL, CENTRAL_SENTINEL_SYMBOL
    parser = argparse.ArgumentParser(
        description='Display run of skew algorithm.')

    parser.add_argument('-i', '--interactive',
                        dest='interactive', action='store_true',
                        help='the visualisation should pause between steps (default).')  # noqa: E501
    parser.add_argument('-n', '--not-interactive',
                        dest='interactive', action='store_false',
                        help='the visualisation should not pause between steps.')        # noqa: E501
    parser.set_defaults(interactive=True)

    parser.add_argument('--term-sentinel', dest='terminal_sentinel',
                        metavar=TERMINAL_SENTINEL_SYMBOL, type=str, default=TERMINAL_SENTINEL_SYMBOL,  # noqa: E501
                        help=f'Symbol to use for the terminal sentinel (default {TERMINAL_SENTINEL_SYMBOL})')  # noqa: E501
    parser.add_argument('--central-sentinel', dest='central_sentinel',
                        metavar=CENTRAL_SENTINEL_SYMBOL, type=str, default=CENTRAL_SENTINEL_SYMBOL,  # noqa: E501
                        help=f'Symbol to use for the central sentinel (default {CENTRAL_SENTINEL_SYMBOL})')  # noqa: E501

    parser.add_argument('x', metavar='string', type=str,
                        help='string to build the suffix array from.')

    args = parser.parse_args()

    INTERACTIVE = args.interactive
    CENTRAL_SENTINEL_SYMBOL = args.central_sentinel
    TERMINAL_SENTINEL_SYMBOL = args.terminal_sentinel

    x, alpha = remap_str(args.x)

    print(colour("Mapping the string to integers")[:, bright_cyan & underline])
    print(map_str(x, alpha), '=>', x)
    print()

    skew_rec(x, alpha)
