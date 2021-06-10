from pystr.sais import sais

from pystr_vis import cols
from pystr_vis import colour, Table, L, R, ColSpec, Align


def test_sa_table() -> None:
    x = "mississippi$"
    sa = sais(x)
    tbl = Table(R, L)
    for i, j in enumerate(sa):
        row = tbl.add_row()
        sa_i = colour(f"sa[{i:>2}] =")[
            :2, cols.bright_blue][3:-3, cols.bright_green]
        suffix = colour(x[j:])[:-1, cols.underline][-1, cols.bright_red]
        row[0] = sa_i
        row[1] = suffix
    print(tbl)


def rotation_table(x: str, sa: list[int]) -> Table:
    tbl = Table(
        ColSpec("pointer", align=Align.RIGHT),
        ColSpec("prefix", right_pad=""),
        ColSpec("rotation")
    )
    for j in sa:
        row = tbl.add_row()
        row["rotation"] = x[j:]+'$'+x[:j]
    return tbl


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(cols.bright_green(name))
            f()
