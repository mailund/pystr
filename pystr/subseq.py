"""Sequence wrappers for constant time slicing."""

from __future__ import annotations
import typing

# Type specifications...
T = typing.TypeVar('T')
# FIXME: I don't know how to make a bound generic
S = typing.TypeVar('S', bound='SubSeq')  # type: ignore
C = typing.TypeVar('C', covariant=True)


class Ordered(typing.Protocol[C]):
    """Types that can be ordered with < and >."""

    def __lt__(self, other: object) -> bool:
        """Must support <."""
        ...  # pragma: no cover

    def __gt__(self, other: object) -> bool:
        """Must support >."""
        ...  # pragma: no cover


# Then the functional stuff...
class SubSeq(typing.Generic[T], typing.Sequence[T]):
    """A wrapper around lists and strings for constant time slicing."""

    _x: typing.Sequence[T]
    _i: int
    _j: int

    @staticmethod
    def _fix_index(x: typing.Sequence[T],
                   start: typing.Optional[int],
                   stop: typing.Optional[int]
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

    def __init__(self,
                 x: typing.Sequence[T],
                 start: typing.Optional[int] = None,
                 stop: typing.Optional[int] = None
                 ) -> None:
        """Construct new subseq from a slice of x."""
        self._x = x
        self._i, self._j = SubSeq._fix_index(x, start, stop)

    def __repr__(self) -> str:  # pragma: no cover
        """Debugging output."""
        cls_name = self.__class__.__name__
        return f"{cls_name}(x={repr(self._x)}, start={self._i}, stop={self._j})"  # noqa: E501

    def __iter__(self) -> typing.Iterator[T]:
        """Iterate through all elements in the subsequence."""
        return (self._x[i] for i in range(self._i, self._j))

    def __len__(self) -> int:
        """Length of the subsequence."""
        return self._j - self._i

    def __bool__(self) -> bool:
        """Is the subsequence non-empty."""
        return self._i < self._j

    def __str__(self) -> str:
        """Get string representation of subsequence."""
        return str(self._x[self._i:self._j])

    def __eq__(self, other: object) -> bool:
        """Test if this object is equilvalent to other."""
        # duck typing from here on... __eq__ must accept all objects
        # but we can only handle sequences.
        # FIXME: Unfortunately, I haven't figured out how to runtime check
        # if an object implements a generic protocol...
        other = typing.cast(typing.Sequence[T], other)
        return len(self) == len(other) and \
            all(a == b for a, b in zip(self, other))

    # You can move this to a mixin if you need to deal with
    # types that do not have an ordering.
    def __lt__(self, other: object) -> bool:
        """Test if self is lexicographically less than other."""
        # duck typing from here on... __eq__ must accept all objects
        # but we can only handle sequences.
        # FIXME: Unfortunately, I haven't figured out how to runtime check
        # if an object implements a generic protocol...
        other = typing.cast(typing.Sequence[Ordered[T]], other)
        for a, b in zip(self, other):
            if a < b:
                return True    # noqal
            if a > b:
                return False   # noqal
        return len(self) < len(other)

    @typing.overload
    def __getitem__(self: S, idx: int) -> T:
        """Get a single element."""
        ...  # pragma: no cover

    @typing.overload
    def __getitem__(self: S, idx: slice) -> S:
        """Get a slice of elements as a subseq."""
        ...  # pragma: no cover

    def __getitem__(self: S, idx: int | slice) -> T | S:
        """Get the value at an index, or a new subseq for a slice."""
        if isinstance(idx, int):
            # FIXME: the cast is needed here because mypy can't
            # figure out generic bound vars, so it doesn't know
            # what type of SubSeq S is.
            return typing.cast(T, self._x[self._i + idx])

        if isinstance(idx, slice):
            assert idx.step is None, \
                "Subsequences do not handle steps in slices"
            i, j = SubSeq._fix_index(self, idx.start, idx.stop)
            return self.__class__(self._x, self._i + i, self._i + j)

        assert False, "idx of invalid type"  # pragma: no cover
        return None  # just for the stupid linter...


class MSubSeq(SubSeq[T]):
    """A subsequence over mutable sequences."""

    _x: typing.MutableSequence[T]  # Make x mutable now...

    # Override init for the type checker...
    def __init__(self, x: typing.MutableSequence[T],
                 start: typing.Optional[int] = None,
                 stop: typing.Optional[int] = None):
        """Create a mutable subsequence from a mutable sequence."""
        super().__init__(x, start, stop)

    def __setitem__(self, idx: int | slice, val: T) -> None:
        """Set an index or a slice to a value."""
        if isinstance(idx, int):
            self._x[self._i + idx] = val
        else:
            # I don't handle steps
            assert isinstance(idx, slice) and idx.step is None
            start, stop = SubSeq._fix_index(self, idx.start, idx.stop)
            for i in range(start, stop):
                self._x[self._i + i] = val
