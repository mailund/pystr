from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Iterable, Iterator, overload, cast
from .cols import ansi_align_left, ansi_align_right, ansifree_len


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


def _copy_spec(col: ColSpec, prefix: str) -> ColSpec:
    return ColSpec(
        name=prefix + col.name,
        left_pad=col.left_pad,
        right_pad=col.right_pad,
        align=col.align
    )


def _copy_cols(tbl: Table, prefix: str) -> tuple[ColSpec, ...]:
    return tuple(_copy_spec(col, prefix) for col in tbl.cols)


L = ColSpec()
R = ColSpec(align=Align.RIGHT)


@dataclass
class Row:
    tbl: Table
    cells: list[str]

    def __iter__(self) -> Iterator[str]:
        return iter(self.cells)

    def __getitem__(self, col: int | str) -> str:
        if isinstance(col, int):
            return self.cells[col]
        else:
            return self.cells[self.tbl.col_names[col]]

    @overload
    def __setitem__(self, col: int, val: object) -> None: ...
    @overload
    def __setitem__(self, col: str, val: object) -> None: ...
    @overload
    def __setitem__(self, col: slice, val: Iterable[object]) -> None: ...

    def __setitem__(self,
                    col: int | slice | str, val: object | Iterable[object]
                    ) -> None:
        if isinstance(col, int):
            self.cells[col] = str(val)
        elif isinstance(col, slice):
            # FIXME: check the length of the val object...
            self.cells[col] = [str(v) for v in cast(Iterable[object], val)]
        else:
            self.cells[self.tbl.col_names[col]] = str(val)


class Table:
    cols: tuple[ColSpec, ...]
    rows: list[Row]
    col_names: dict[str, int]

    def __init__(self, *cols: ColSpec) -> None:
        self.cols = cols
        self.rows = []

        self.col_names = {
            col.name: i for i, col in enumerate(self.cols)
        }

    def __getitem__(self, i: int) -> Row:
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

        def left(w: int) -> Callable[[str], str]:
            return lambda x: ansi_align_left(x, w)

        def right(w: int) -> Callable[[str], str]:
            return lambda x: ansi_align_right(x, w)

        for i in range(len(colw)):
            # FIXME: pattern match this when mypy can handle it
            if self.cols[i].align is Align.LEFT:
                formatters.append(left(colw[i]))
            elif self.cols[i].align is Align.RIGHT:
                formatters.append(right(colw[i]))
            else:  # pragma: no cover
                assert False, "Unknown alignment"
        return formatters

    def __str__(self) -> str:
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

    def __iter__(self) -> Iterator[Row]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __or__(self, other: Table) -> Table:
        new = Table(*(_copy_cols(self, "1_")+_copy_cols(other, "2_")))
        n1, n2 = len(self.cols), len(other.cols)
        m = max(len(self), len(other))
        for _ in range(m):
            new.add_row()
        for i in range(len(self)):
            new[i][0:n1] = self[i].cells
        for i in range(len(other)):
            new[i][n1:n1+n2] = other[i].cells
        return new
