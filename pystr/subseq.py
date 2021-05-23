from __future__ import annotations
from collections.abc import Iterator
from typing import Generic, TypeVar, Optional
from typing import Sequence, MutableSequence
from typing import overload

# Type specifications...
T = TypeVar('T')
S = TypeVar('S', bound="subseq")


# Then the functional stuff...
class subseq(Generic[T]):
    """This is a wrapper around lists and strings that lets us slice them
without copying them.
"""
    _x: Sequence[T]
    _i: int
    _j: int

    def __init__(self, x: Sequence[T],
                 start: Optional[int] = None,
                 stop: Optional[int] = None):
        self._x = x
        self._i = start if start is not None else 0
        self._j = stop if stop is not None else len(x)

        assert self._i <= self._j, "Start must come before end."
        assert 0 <= self._i <= len(self._x), \
            "Indices must be within the sequence's range."
        assert 0 <= self._j <= len(self._x), \
            "Indices must be within the sequence's range."

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(x={repr(self._x)}, start={self._i}, stop={self._j})" # noqal

    def __iter__(self) -> Iterator[T]:
        return (self._x[i] for i in range(self._i, self._j))

    def __len__(self) -> int:
        return self._j - self._i

    def __bool__(self) -> bool:
        return self._i < self._j

    def __str__(self) -> str:
        return str(self._x[self._i:self._j])

    def __eq__(self, other) -> bool:
        return len(self) == len(other) and \
            all(a == b for a, b in zip(self, other))

    # You can move this to a mixin if you need to deal with
    # types that do not have an ordering.
    def __lt__(self, other):
        for a, b in zip(self, other):
            if a < b: return True    # noqal
            if a > b: return False   # noqal
        return len(self) < len(other)

    @overload
    def __getitem__(self: S, idx: int) -> T: ...
    @overload
    def __getitem__(self: S, idx: slice) -> S: ...

    def __getitem__(self: S, idx: int | slice) -> T | S:
        if isinstance(idx, int):
            return self._x[self._i + idx]

        if isinstance(idx, slice):
            i: int = idx.start if idx.start is not None else 0
            j: int = idx.stop if idx.stop is not None else len(self)
            return self.__class__(self._x, self._i + i, self._i + j)


class msubseq(subseq[T]):
    _x: MutableSequence[T]  # Make x mutable now...

    # Override init for the type checker...
    def __init__(self, x: MutableSequence[T],
                 start: Optional[int] = None,
                 stop: Optional[int] = None):
        super().__init__(x, start, stop)

    def __setitem__(self, idx: int | slice, val: T):
        if isinstance(idx, int):
            self._x[self._i + idx] = val
        else:
            # I don't handle steps
            assert isinstance(idx, slice) and idx.step is None
            start = idx.start if idx.start is not None else 0
            stop = idx.stop if idx.stop is not None else len(self)
            for i in range(start, stop):
                self._x[self._i + i] = val


# Frequently used subsequences... The inheritance pattern here
# reflects that a mutable version over a type should be castable
# to an immutable.
substr = subseq[str]
isseq = subseq[int]
misseq = msubseq[int]
