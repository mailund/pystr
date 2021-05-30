import _setup  # noqa: F401

from pystr.sais import sais
from pystr.cols import underline, bright_yellow, bold, black, red
from pystr.cols import bright_red, bright_green, bright_blue, green
from pystr.output import colour, Table, L, R, ColSpec
from pystr.bwt import c_table, o_table


def test_sa_table():
    x = "mississippi$"
    sa = sais(x)
    tbl = Table(R, L)
    for i, j in enumerate(sa):
        row = tbl.add_row()
        sa_i = colour(f"sa[{i:>2}] =")[:2, bright_blue][3:-3, bright_green]
        suffix = colour(x[j:])[:-1, underline][-1, bright_red]
        row[0] = sa_i
        row[1] = suffix
    print(tbl)


def rotation_table(x: str, sa: list[int]):
    tbl = Table(
        ColSpec("pointer"),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for i, j in enumerate(sa):
        row = tbl.add_row()
        row["rotation"] = x[j:]+'$'+x[:j]
    return tbl


def test_bwt():
    k, a = 3, "s"
    x = "mississippi"
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

    print(bright_blue(
        f"{underline}Prepending the prefix (and drop the suffix):"))
    print()
    tbl = rotation_table(x, sa)
    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["prefix"] = bright_green(a)
    tbl[k]["rotation"] = colour(tbl[k]["rotation"])[0:-1, underline][-1, black]
    print(tbl)
    print()

    print(bright_blue(
        f"{underline}Find the bucket:"))
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

    print(bright_blue(
        f"{underline}Count offset:"))
    print()
    tbl = rotation_table(x, sa)
    # FIXME: handle overlapping pointers
    tbl[k]["pointer"] = bold("k ->")
    tbl[k]["prefix"] = bright_green(a)
    tbl[k]["rotation"] = colour(tbl[k]["rotation"])[
        0:-1, underline & bright_yellow][-1, black]

    tbl[ctab[a]]["pointer"] = bright_blue(f"C[{a}] ->")

    for i in range(k):
        row = tbl[i]
        if row["rotation"].endswith(a):
            row["rotation"] = \
                colour(row["rotation"])[:-1, underline & red][-1, bright_green]

    for i in range(ctab[a], ctab[a]+otab[a][k]):
        row = tbl[i]
        row["rotation"] = colour(row["rotation"])[
            0, bright_green][1:, underline & red]

    row = tbl[ctab[a]+otab[a][k]]
    row["pointer"] = bright_blue(f"C[{a}]") + " + " + \
        bright_green(f"O[{a},{k}]") + " ->"
    row["rotation"] = \
        colour(row["rotation"])[0, bright_green][1:, underline & bright_yellow]

    print(tbl)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(bright_green(name))
            f()
