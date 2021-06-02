import argparse

from typing import Callable, Any

from pystr import sais
from pystr.bwt import c_table, o_table

from pystr_vis import colour, Table, ColSpec, Align
from pystr_vis.tables import Row
from pystr_vis.cols import \
    strip_ansi, \
    underline, bold, \
    bright_blue, bright_green,  \
    black, green, magenta, red, blue


def hit_enter():
    input("Press ENTER to continue")


def rotation_table(x: str, sa: list[int]):
    tbl = Table(
        ColSpec("pointer", align=Align.RIGHT),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation"),
        ColSpec("r_pointer")
    )
    for j in sa:
        row = tbl.add_row()
        row["rotation"] = x[j:]+'$'+x[:j]
    return tbl


def rot_row(row: Row, a: str):
    rot = strip_ansi(row["rotation"])
    if rot[-1] == a:
        row["prefix"] = green(a)
        row["rotation"] = colour(rot[:-1])[:, underline]
    else:
        row["rotation"] = colour(rot)[-1, red]


def shift_row(row: Row):
    rot = strip_ansi(row["rotation"])
    row["prefix"] = green(rot[0])
    row["rotation"] = colour(rot[1:])[:, underline]


# FIXME: Figure out how to specify that f should take a row
# as its first argument and then *args...
def map_rows(tbl: Table, start: int, stop: int,
             f: Callable[..., Any], *args: Any):
    for i in range(start, stop):
        f(tbl[i], *args)


def rot_rows(tbl: Table, a: str, start: int, stop: int):
    map_rows(tbl, start, stop, rot_row, a)


def shift_rows(tbl: Table, start: int, stop: int):
    map_rows(tbl, start, stop, shift_row)


def show_bwt_transition():

    parser = argparse.ArgumentParser(
        description='Show one transition, (i, "a") -> C["a"] + O["a", i], in the BWT search.')  # noqa: E501

    parser.add_argument('-i', '--interactive',
                        dest='interactive', action='store_true',
                        help='the visualisation should pause between steps (default).')  # noqa: E501
    parser.add_argument('-n', '--not-interactive',
                        dest='interactive', action='store_false',
                        help='the visualisation should not pause between steps.')        # noqa: E501
    parser.set_defaults(interactive=True)

    parser.add_argument('x', metavar='x', type=str,
                        help='string the BWT rotations are made over.')
    parser.add_argument('k', metavar='k', type=int,
                        help='current index.')
    parser.add_argument('a', metavar='a', type=str,
                        help='character to prepend.')

    args = parser.parse_args()
    if len(args.a) != 1:
        print("The prepend-character 'a' must have length 1. " +
              f"You provided '{args.a}'")
        import sys
        sys.exit(1)
    if not (0 <= args.k <= len(args.x)):
        print(f"The index variable k={args.k} must be in the range " +
              f"[0,{len(args.x)}] (a valid index in the rotations).")
        import sys
        sys.exit(1)
    if args.a not in args.x:
        print(f"The character {args.a} is not in the string.")
        import sys
        sys.exit(1)

    x, k, a = args.x, args.k, args.a

    sa = sais(x, include_sentinel=True)
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())

    print()
    print(bright_blue(f"{underline}String we want to jump from:"))
    print()
    tbl = rotation_table(x, sa)
    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["rotation"] = underline(tbl[k]["rotation"])
    print(tbl)
    print()
    if args.interactive:
        hit_enter()
        print()

    print(bright_blue(
        f"{underline}Attempted rotation:"))
    print()
    tbl = rotation_table(x, sa)
    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["prefix"] = bright_green(a)
    tbl[k]["rotation"] = colour(tbl[k]["rotation"])[0:-1, underline][-1, black]
    print(tbl)
    print()
    if args.interactive:
        hit_enter()
        print()

    print(bright_blue(f"{underline}Find the bucket:"))
    print()
    tbl = rotation_table(x, sa)
    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["prefix"] = bright_green(a)
    tbl[k]["rotation"] = colour(tbl[k]["rotation"])[0:-1, underline][-1, black]

    tbl[ctab[a]]["pointer"] = green(f"C[{a}] ->")
    for i in range(ctab[a], len(sa)):
        row = tbl[i]
        if not row["rotation"].startswith(a):
            break
        row["rotation"] = green(row["rotation"])
    print(tbl)
    print()
    if args.interactive:
        hit_enter()
        print()

    print(bright_blue(f"{underline}Count offset:"))
    print()
    tbl = rotation_table(x, sa)
    rot_rows(tbl, a, 0, k)

    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["prefix"] = bright_green(a)
    tbl[k]["rotation"] = colour(tbl[k]["rotation"])[
        0:-1, blue & underline][-1, black]

    print(tbl)
    print()
    if args.interactive:
        hit_enter()
        print()

    print(bright_blue(f"{underline}Done:"))
    print()
    res_tbl = rotation_table(x, sa)
    shift_rows(res_tbl, ctab[a], ctab[a] + otab[a][k])

    res_tbl[ctab[a]]["pointer"] = green(f"C[{a}] ->")

    hit_idx = ctab[a]+otab[a][k]
    if hit_idx < len(tbl):
        row = res_tbl[hit_idx]
        row["pointer"] = green(f"C[{a}]") + " + " + \
            magenta(f"O[{a},{k}]") + " ->"

        target = a + strip_ansi(tbl[k]["rotation"])[:-1]
        hit = strip_ansi(tbl[hit_idx]["prefix"]) + \
            strip_ansi(tbl[hit_idx]["rotation"])
        match_col = green if target == hit else red

        shift_row(row)
        row["rotation"] = colour(row["rotation"])[:, underline & match_col]

    else:
        # We are pointing one past the range...
        row = res_tbl.add_row()
        row["pointer"] = green(f"C[{a}]") + " + " + \
            magenta(f"O[{a},{k}]") + " ->"

    print()
    print(tbl | res_tbl)
    print()


def show_bwt_search():

    x = 'mississippi'  # FIXME
    p = 'ssi'

    sa = sais(x, include_sentinel=True)
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())

    L = 0  # Starting at 0 (the sentinel) handles empty strings
    R = len(x) + 1  # +1 because of the sentinel
    for y in p[::-1]:
        if y not in ctab:
            return 0, 0
        L = ctab[y] + otab[y][L]
        R = ctab[y] + otab[y][R]
        if L >= R:
            return 0, 0
