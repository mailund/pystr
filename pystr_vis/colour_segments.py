from typing import NamedTuple
from collections import deque
from .cols import Colour, plain, strip_ansi


def clamp_index(x: str, i: int) -> int:
    if i < 0:  # adjust negative index
        i += len(x)
    return min(max(0, i), len(x))


_ColourSegment = NamedTuple(
    "_ColourSegment",
    [("start", int), ("stop", int), ("col", Colour)]
)


# This makes debugging a little nicer...
class ColourSegment(_ColourSegment):  # pragma: no cover -- just for debugging
    def __str__(self):
        return self.col(f"[{self.start},{self.stop})")
    __repr__ = __str__


# There must be a better way to handle overlapping intervals,
# but segmented text is short and I am ok with a hack that's
# fast to impement...
# This function merges lists of sorted non-overlapping segments
# and with divide and conquer I get segmentation in O(n log n).
def merge_segments(x: list[ColourSegment], y: list[ColourSegment]) \
        -> list[ColourSegment]:

    res: list[ColourSegment] = []
    while x and y:
        a, b = x.pop(), y.pop()

        if b.start >= a.stop:
            # we can emit all of b and keep a
            res.append(b)
            x.append(a)
        elif a.start >= b.stop:
            # we can emit all of a and keep b
            res.append(a)
            y.append(b)

        elif a.stop < b.stop:
            # emit the non-overlapping part of b
            res.append(ColourSegment(a.stop, b.stop, b.col))
            if b.start < a.stop:  # if there is something left of b, keep it
                y.append(ColourSegment(b.start, a.stop, b.col))
            x.append(a)  # keep a

        elif b.stop < a.stop:
            # emit the non-overlapping part of a
            res.append(ColourSegment(b.stop, a.stop, a.col))
            if a.start < b.stop:  # if there is something left of b, keep it
                x.append(ColourSegment(a.start, b.stop, a.col))
            y.append(b)  # keep b

        elif a.stop == b.stop:
            # Now we split based on the starting point
            if a.start < b.start:
                # emit b and reduce a
                res.append(b)
                x.append(ColourSegment(a.start, b.start, a.col))
            else:
                # emit a and reduce b
                res.append(a)
                y.append(ColourSegment(b.start, a.start, b.col))

        else:  # pragma: no cover
            assert False, "We should have handled all cases"

    res.extend(reversed(x))
    res.extend(reversed(y))
    res = res[::-1]

    # FIXME: remove this check when I'm more sure that the merge works...
    for i in range(len(res) - 1):
        assert res[i].stop <= res[i+1].start

    return res


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

    def _split_segments(self):
        assert self.segments, "Should only be called with non-empty segments"

        queue = deque([seg] for seg in self.segments)
        while len(queue) > 1:
            queue.append(merge_segments(queue.popleft(), queue.popleft()))
        self.segments = queue[0]

    def _complete_segments(self):
        if not self.segments:
            return

        self._split_segments()
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
        self._complete_segments()
        return "".join(
            str(col(self.x[start:stop]))
            for start, stop, col in self.segments
        )
