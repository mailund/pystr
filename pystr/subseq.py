from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, Generic, TypeVar, Optional
from typing import overload, cast

# Type specifications...
T = TypeVar('T')
S = TypeVar('S', covariant=True)
R = TypeVar('R', contravariant=True)


class Sliceable(Protocol[S]):
    def __len__(self) -> int: ...

    @overload
    def __getitem__(self, i: int) -> S: ...
    @overload
    def __getitem__(self, i: slice) -> Sliceable[S]: ...


class MutSlicable(Sliceable, Protocol[R]):
    # FIXME: handle when val is not a single value
    @overload
    def __setitem__(self, i: int, val: R): ...
    @overload
    def __setitem__(self, i: slice, val: R): ...


# Then the functional stuff...
class subseq_mixin(Generic[T]):

    # These will be set in the subclass.
    x: Sliceable[T]
    i: int = 0
    j: int = -1

    def __post_init__(self) -> None:
        if self.j == -1:
            # Hack around frozen to get a default j that depends
            # on the length of x.
            object.__setattr__(self, "j", len(self.x))

        assert self.i <= self.j, "Start must come before end."
        # The legal range for indices is zero to
        # the length of the string. Notice that this
        # allows indices one beyond the last character.
        # That is usually how an end-index matches the
        # end of the string, but to handle empty strings
        # we allow it for the start index as well.
        assert 0 <= self.i <= len(self.x), \
            "Slices must be within the string's range."
        assert 0 <= self.j <= len(self.x), \
            "Slices must be within the string's range."

    # Pattern matching would be the way to implement this, but
    # mypy still crashes with them. I'll rewrite this when it catches
    # up with Python 3.10.
    def __getitem__(self, idx):
        if type(idx) == int:
            return self.x[self.i + idx]

        if type(idx) == slice:
            i: Optional[int] = idx.start
            j: Optional[int] = idx.stop
            if i is None and j is None:
                return self
            if i is not None and j is None:
                return self.__class__(self.x, self.i + i, self.j)
            if i is None and j is not None:
                return self.__class__(self.x, self.i, self.i + j)
            else:
                return self.__class__(self.x,
                                      self.i + cast(int, i),
                                      self.i + cast(int, j))

        assert False, \
            f"Index {idx} wasn't a valid type."  # pragma: no coverage

    def __str__(self) -> str:
        return str(self.x[self.i:self.j])

    def __iter__(self) -> Iterator[T]:
        return (self.x[i] for i in range(self.i, self.j))

    def __len__(self) -> int:
        return self.j - self.i

    def __bool__(self) -> bool:
        return self.i < self.j

    def __eq__(self, other) -> bool:
        return len(self) == len(other) and \
            all(a == b for a, b in zip(self, other))


@dataclass(frozen=True, eq=False)
class subseq(subseq_mixin[T]):
    """This is a wrapper around lists and strings that lets us slice them
without copying them.
"""
    x: Sliceable[T]  # Maybe separate mutable/immutable ?
    i: int = 0
    j: int = -1

    # These are needed to inform the type checker about the
    # two different return types for indexing/slicing.
    @overload
    def __getitem__(self, _: int) -> T: ...
    @overload
    def __getitem__(self, _: slice) -> subseq[T]: ...

    def __getitem__(self, idx):
        return super().__getitem__(idx)


@dataclass(frozen=True, eq=False)
class mutsubseq(subseq_mixin[T]):
    x: MutSlicable[T]
    i: int = 0
    j: int = -1

    # These are needed to inform the type checker about the
    # two different return types for indexing/slicing.
    @overload
    def __getitem__(self, _: int) -> T: ...
    @overload
    def __getitem__(self, _: slice) -> mutsubseq[T]: ...

    def __getitem__(self, idx):
        return super().__getitem__(idx)

    # FIXME: type overloading
    # FIXME: I haven't handled if the right-hand-side isn't a scalar
    def __setitem__(self, idx: int | slice, val: T):
        if type(idx) == int:
            self.x[self.i + idx] = val
        else:
            assert type(idx) == slice
            start, stop, step = idx.start, idx.stop, idx.step
            if start is None:
                start = 0
            if stop is None:
                stop = len(self)
            if step is None:
                step = 1
            for i in range(start, stop, step):
                self.x[self.i + i] = val


# Special name for subseq[str]
substr = subseq[str]
