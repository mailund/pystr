from enum import Enum, auto
from typing import NamedTuple
from typing import Protocol
from .cols import Colour, plain


class Formattable(Protocol):
    def __len__(self): ...
    def __str__(self): ...


def indent(i: int):
    return ' ' * i


def out(*xs: Formattable):
    for x in xs:
        print(x, sep="", end="")
    print()


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
        self.x = x
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

    def __len__(self):
        return len(self.x)  # len without ansi codes

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


class table:
    cols: tuple[Align, ...]
    rows: list[tuple[Formattable, ...]]
    colsep: str

    def __init__(self, *cols: Align, colsep=' '):
        self.cols = cols
        self.rows = []
        self.colsep = colsep

    def __getitem__(self, row: tuple[Formattable, ...]):
        assert len(row) == len(self.cols), \
            "Each row must have a column for each column in the table."
        self.rows.append(row)
        return self

    def _get_col_widths(self) -> list[int]:
        widths = [0] * len(self.cols)
        for row in self.rows:
            for i, c in enumerate(row):
                widths[i] = max(widths[i], len(c))
        return widths

    def _format_strings(self) -> list[str]:
        colw = self._get_col_widths()
        fmt_strings: list[str] = []
        for i in range(len(colw)):
            if self.cols[i] is Align.LEFT:
                fmt_strings.append("{"+f":{colw[i]}"+"}")
            if self.cols[i] is Align.RIGHT:
                fmt_strings.append("{"+f":>{colw[i]}"+"}")
        return fmt_strings

    def __str__(self):
        fmt_strings = self._format_strings()
        rows = []
        for row in self.rows:
            rows.append(
                self.colsep.join(fmt.format(str(x))
                                 for fmt, x in zip(fmt_strings, row))
            )
        return "\n".join(rows)
