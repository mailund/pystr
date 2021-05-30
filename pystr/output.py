# from dataclasses import dataclass
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
            col(self.x[start:stop])
            for start, stop, col in self.segments
        )
