from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable
from .cols import ansifree_len


class Align(Enum):
    LEFT = auto()
    RIGHT = auto()
    # fuck centre! (I don't need it now)


@dataclass(frozen=True)
class ColSpec:
    name: str = ""
    left_pad: str = ""
    right_pad: str = " "
    align: Align = Align.LEFT


L = ColSpec()
R = ColSpec(align=Align.RIGHT)


@dataclass
class Row:
    tbl: Table
    cells: list[str]

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, col: int | str) -> str:
        if isinstance(col, int):
            return self.cells[col]
        else:
            return self.cells[self.tbl.col_names[col]]

    def __setitem__(self, col: int | str, val: str):
        if isinstance(col, int):
            self.cells[col] = str(val)
        else:
            self.cells[self.tbl.col_names[col]] = str(val)


class Table:
    cols: tuple[ColSpec, ...]
    rows: list[Row]
    col_names: dict[str, int]

    def __init__(self, *cols: ColSpec):
        self.cols = cols
        self.rows = []

        self.col_names = {
            col.name: i for i, col in enumerate(self.cols)
        }

    def __getitem__(self, i: int):
        return self.rows[i]

    def append_row(self, *cells: str) -> Table:
        row = self.add_row()
        for i, x in enumerate(cells):
            row[i] = x
        return self  # For chaining

    def add_row(self) -> Row:
        row = Row(self, [""] * len(self.cols))
        self.rows.append(row)
        return row

    def _get_col_widths(self) -> list[int]:
        widths = [0] * len(self.cols)
        for row in self.rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], ansifree_len(cell))
        return widths

    def _formatters(self) -> list[Callable[[str], str]]:
        colw = self._get_col_widths()
        formatters: list[Callable[[str], str]] = []
        def left(w): return lambda x: x + ' ' * (w - ansifree_len(x))
        def right(w): return lambda x: ' ' * (w - ansifree_len(x)) + x
        for i in range(len(colw)):
            # FIXME: pattern match this when mypy can handle it
            if self.cols[i].align is Align.LEFT:
                formatters.append(left(colw[i]))
            elif self.cols[i].align is Align.RIGHT:
                formatters.append(right(colw[i]))
            else:
                assert False, "Unknown alignment"
        return formatters

    def __str__(self):
        formatters = self._formatters()
        rows = []
        for row in self.rows:
            rows.append(
                "".join(
                    cspec.left_pad+fmt(x)+cspec.right_pad
                    for fmt, cspec, x in zip(formatters, self.cols, row)
                )
            )
        return "\n".join(rows)

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)
