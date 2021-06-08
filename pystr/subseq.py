from __future__ import annotations
from collections.abc import Iterator
from typing import Generic, TypeVar, Protocol
from typing import Optional, Sequence, MutableSequence
from typing import overload, cast

# Type specifications...
T = TypeVar('T')
S = TypeVar('S', bound="subseq")

C = TypeVar('C', covariant=True)


class Ordered(Protocol[C]):
    def __lt__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...


# Then the functional stuff...
class subseq(Generic[T], Sequence[T]):
    """This is a wrapper around lists and strings that lets us slice them
without copying them.
"""
    _x: Sequence[T]
    _i: int
    _j: int

    @staticmethod
    def _fix_index(x: Sequence[T],
                   start: Optional[int],
                   stop: Optional[int]
                   ) -> tuple[int, int]:
        start = start if start is not None else 0
        stop = stop if stop is not None else len(x)
        if start < 0:
            start += len(x)
        if stop < 0:
            stop += len(x)

        assert start <= stop, "Start must come before end."
        assert 0 <= start <= len(x), \
            "Indices must be within the sequence's range."
        assert 0 <= stop <= len(x), \
            "Indices must be within the sequence's range."

        return start, stop

    # Mypy doesn't like me to access __init__() directly,
    # so this is a hack to have init outside of __init__
    def _init(self, x: Sequence[T],
              start: Optional[int] = None,
              stop: Optional[int] = None) -> None:
        self._x = x
        self._i, self._j = subseq._fix_index(x, start, stop)

    def __init__(self, x: Sequence[T],
                 start: Optional[int] = None,
                 stop: Optional[int] = None) -> None:
        self._init(x, start, stop)

    def __repr__(self) -> str:  # pragma: no cover
        cls_name = self.__class__.__name__
        return f"{cls_name}(x={repr(self._x)}, start={self._i}, stop={self._j})"  # noqa: E501

    def __iter__(self) -> Iterator[T]:
        return (self._x[i] for i in range(self._i, self._j))

    def __len__(self) -> int:
        return self._j - self._i

    def __bool__(self) -> bool:
        return self._i < self._j

    def __str__(self) -> str:
        return str(self._x[self._i:self._j])

    def __eq__(self, other: object) -> bool:
        # duck typing from here on... __eq__ must accept all objects
        # but we can only handle sequences.
        # FIXME: Unfortunately, I haven't figured out how to runtime check
        # if an object implements a generic protocol...
        other = cast(Sequence[T], other)
        return len(self) == len(other) and \
            all(a == b for a, b in zip(self, other))

    # You can move this to a mixin if you need to deal with
    # types that do not have an ordering.
    def __lt__(self, other: object) -> bool:
        # duck typing from here on... __eq__ must accept all objects
        # but we can only handle sequences.
        # FIXME: Unfortunately, I haven't figured out how to runtime check
        # if an object implements a generic protocol...
        other = cast(Sequence[Ordered[T]], other)
        for a, b in zip(self, other):
            if a < b:
                return True    # noqal
            if a > b:
                return False   # noqal
        return len(self) < len(other)

    @overload
    def __getitem__(self: S, idx: int) -> T: ...
    @overload
    def __getitem__(self: S, idx: slice) -> S: ...

    def __getitem__(self: S, idx: int | slice) -> T | S:
        if isinstance(idx, int):
            return self._x[self._i + idx]

        if isinstance(idx, slice):
            i, j = subseq._fix_index(self, idx.start, idx.stop)
            new_subseq = self._new_object()
            self.init_clone(new_subseq, self._x,
                            self._i + i, self._i + j)
            return new_subseq

    def _new_object(self: S) -> S:
        return self.__class__.__new__(self.__class__)

    def init_clone(self: S, clone: S,
                   x: Sequence[T], start: int, stop: int) -> None:
        # This method just gives you a way to modify an object
        # that is the result of a slice, instead of only calling
        # the init method. Think of it as an alternative __init__.
        clone._init(x, start, stop)


class msubseq(subseq[T]):
    _x: MutableSequence[T]  # Make x mutable now...

    # Override init for the type checker...
    def __init__(self, x: MutableSequence[T],
                 start: Optional[int] = None,
                 stop: Optional[int] = None):
        super().__init__(x, start, stop)

    def __setitem__(self, idx: int | slice, val: T) -> None:
        if isinstance(idx, int):
            self._x[self._i + idx] = val
        else:
            # I don't handle steps
            assert isinstance(idx, slice) and idx.step is None
            start, stop = subseq._fix_index(self, idx.start, idx.stop)
            for i in range(start, stop):
                self._x[self._i + i] = val


# Frequently used subsequences... The inheritance pattern here
# reflects that a mutable version over a type should be castable
# to an immutable.
substr = subseq[str]
isseq = subseq[int]
misseq = msubseq[int]
