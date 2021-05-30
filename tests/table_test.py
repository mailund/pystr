import _setup  # noqa: F401

from pystr.sais import sais
from pystr.cols import underline, bright_yellow, bold, black, green
from pystr.cols import bright_red, bright_green, bright_blue, blue
from pystr.output import Align
from pystr.output import colour, Table, L, R, ColSpec
from pystr.bwt import CTAB, OTAB, c_table, o_table


def test_trivial_table():
    tbl = Table(L, L, R)
    tbl.append_row("", "foo", "bar")
    tbl.append_row("sa[i] ->", "baz", "qux")
    tbl.append_row("", "foobar", "x")
    print(tbl)


def test_sa_table():
    x = "mississippi$"
    sa = sais(x)
    tbl = Table(R, L)
    for i, j in enumerate(sa):
        sa_i = colour(f"sa[{i:>2}] =")[:2, bright_blue][3:-3, bright_green]
        suffix = colour(x[j:])[:-1, underline][-1, bright_red]
        tbl.append_row(sa_i, suffix)
    print(tbl)


def test_bwt():
    k, a = 3, "s"
    x = "mississippi"
    sa = sais(x, include_sentinel=True)
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())

    print()
    print(bright_blue(f"{underline}String we want to jump from:"))
    print()
    tbl = Table(
        ColSpec("pointer"),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for i, j in enumerate(sa):
        row = tbl.next_row()
        row["rotation"] = x[j:]+'$'+x[:j]
        if i == k:
            row["pointer"] = bold("k ->")
            row["rotation"] = underline(row["rotation"])
    print(tbl)
    print()

    print(bright_blue(
        f"{underline}Prepending the prefix (and drop the suffix):"))
    print()
    tbl = Table(
        ColSpec("pointer"),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    target = a+x[sa[k]:]+x[:sa[k]-1]
    for i, j in enumerate(sa):
        row = tbl.next_row()
        row["rotation"] = x[j:]+'$'+x[:j]
        if target == row["rotation"]:
            row["rotation"] = blue(row["rotation"])
        if i == k:
            row["pointer"] = bold("k ->")
            row["prefix"] = bright_yellow(a)
            row["rotation"] = colour(row["rotation"])[
                :-1, underline][-1, black]
    print(tbl)
    print()

    print(bright_blue(
        f"{underline}Find the bucket:"))
    print()
    tbl = Table(
        ColSpec("pointer", align=Align.RIGHT),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for i, j in enumerate(sa):
        row = tbl.next_row()
        rotation = x[j:]+'$'+x[:j]
        row["rotation"] = \
            green(rotation) if rotation.startswith(a) else rotation
        if i == k:
            row["pointer"] = "k ->"  # FIXME: bold("k ->")
        if i == ctab[a]:
            row["pointer"] = bright_green(f"C[{a}] ->")
    print(tbl)
    print()

    print(bright_blue(
        f"{underline}Count offset:"))
    print()
    tbl = Table(
        ColSpec("pointer"),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for i, j in enumerate(sa):
        row = tbl.next_row()
        row["rotation"] = x[j:]+'$'+x[:j]
        if i < k:
            if row["rotation"].endswith(a):
                row["rotation"] = \
                    colour(row["rotation"])[:-1, blue][-1, bright_green]
            else:
                row["rotation"] = blue(row["rotation"])
        if i == k:
            row["pointer"] = bold("k ->")
            row["prefix"] = bright_yellow(a)
            row["rotation"] = colour(row["rotation"])[
                :-1, underline][-1, black]
    print(tbl)
    print()
    print(bright_blue(
        f"{underline}Use bucket start and offset:"))
    print()
    tbl = Table(
        ColSpec("pointer", align=Align.RIGHT),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for i, j in enumerate(sa):
        row = tbl.next_row()
        row["rotation"] = x[j:]+'$'+x[:j]
        row["rotation"] = \
            green(rotation) if rotation.startswith(a) else rotation
        if i == ctab[a]:
            row["pointer"] = colour(f"C[{a}] ->")[:, bright_green]
        if i == ctab[a] + otab[a][k]:
            row["pointer"] = colour(f"C[{a}] + O[{a},{k}] ->")[:, bright_blue]

    print(tbl)
    print()


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(bright_green(name))
            f()
