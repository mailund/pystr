from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple, Callable, Any
from .cols import Colour, plain, strip_ansi, ansifree_len


def out(*xs: Any):  # FIXME: maybe get rid of this
    for x in xs:
        print(str(x), sep="", end="")
    print()


def indent(i: int):
    return ' ' * i


def clamp_index(x: str, i: int) -> int:
    if i < 0:  # adjust negative index
        i += len(x)
    return min(max(0, i), len(x))


ColourSegment = NamedTuple(
    "ColourSegment",
    [("start", int), ("stop", int), ("col", Colour)]
)


class colour:
    x: str
    segments: list[ColourSegment]

    def __init__(self, x: str):
        self.x = strip_ansi(x)
        self.segments = []

    def __getitem__(self, arg: tuple[int | slice, Colour]):
        i, col = arg
        if isinstance(i, int):
            start = i if i >= 0 else i + len(self.x)
            stop = start + 1
        else:
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self.x)

            # should be clamp method
            if start < 0:
                start += len(self.x)
            if stop < 0:
                stop += len(self.x)

        self.segments.append(
            ColourSegment(
                clamp_index(self.x, start),
                clamp_index(self.x, stop),
                col
            )
        )
        return self

    def complete_segments(self):
        if not self.segments:
            return
        self.segments.sort(key=lambda seg: seg.start)
        res: list[ColourSegment] = []
        cur: int = 0
        for seg in self.segments:
            assert seg.start >= cur, \
                "We cannot colour overlapping segments"
            if cur < seg.start:
                res.append(ColourSegment(cur, seg.start, plain))
            res.append(seg)
            cur = seg.stop
        if cur < len(self.x):
            res.append(ColourSegment(cur, len(self.x), plain))
        self.segments = res

    def __str__(self):
        self.complete_segments()
        return "".join(
            str(col(self.x[start:stop]))
            for start, stop, col in self.segments
        )


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
