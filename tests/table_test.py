import _setup  # noqa: F401

from pystr.sais import sais
from pystr.cols import red, bright_red, underline, bright_green, bright_blue
from pystr.output import colour, table, Align


def test_trivial_table():
    tbl = table(Align.LEFT, Align.LEFT, Align.RIGHT)
    tbl["", "foo", "bar"]
    tbl[red("sa[i] ->"), "baz", "qux"]
    tbl["", "foobar", "x"]
    print(tbl)


def test_sa_table():
    x = "mississippi$"
    sa = sais(x)
    tbl = table(Align.RIGHT, Align.LEFT)
    for i, j in enumerate(sa):
        sa_i = colour(f"sa[{i:>2}] =")[:2, bright_blue][3:-3, bright_green]
        suffix = colour(x[j:])[:-1, underline][-1, bright_red]
        tbl[sa_i, suffix]
    print(tbl)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(bright_green(name))
            f()
