from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar, Optional
from typing import Sized, Sequence, MutableSequence
from typing import overload, cast

# Type specifications...
T = TypeVar('T')
S = TypeVar('S', bound="subseq")


class SizedIterable(Sized, Iterable[T]):
    ...


# Then the functional stuff...
@dataclass(frozen=True, eq=False)
class subseq(Generic[T]):
    """This is a wrapper around lists and strings that lets us slice them
without copying them.
"""
    x: Sequence[T]  # Maybe separate mutable/immutable ?
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
            "Indices must be within the sequence's range."
        assert 0 <= self.j <= len(self.x), \
            "Indices must be within the sequence's range."

    def __iter__(self) -> Iterator[T]:
        return (self.x[i] for i in range(self.i, self.j))

    def __len__(self) -> int:
        return self.j - self.i

    def __bool__(self) -> bool:
        return self.i < self.j

    def __str__(self):
        return str(self.x[self.i:self.j])

    def __eq__(self, other) -> bool:
        return len(self) == len(other) and \
            all(a == b for a, b in zip(self, other))

    @overload
    def __getitem__(self: S, idx: int) -> T: ...
    @overload
    def __getitem__(self: S, idx: slice) -> S: ...

    def __getitem__(self: S, idx: int | slice) -> T | S:
        if isinstance(idx, int):
            return self.x[self.i + idx]

        if isinstance(idx, slice):
            i: Optional[int] = idx.start
            j: Optional[int] = idx.stop
            if i is None and j is None:
                return self
            if i is not None and j is None:
                return self.__class__(self.x, self.i + i, self.j)
            if i is None and j is not None:
                return self.__class__(self.x, self.i, self.i + j)
            else:
                assert i is not None and j is not None  # for the type checker
                return self.__class__(self.x, self.i + i, self.i + j)


@dataclass(frozen=True, eq=False)
class msubseq(subseq[T]):
    x: MutableSequence[T]
    i: int = 0
    j: int = -1

    def __setitem__(self, idx: int | slice, val: T):
        if isinstance(idx, int):
            self.x[self.i + idx] = val
        else:
            # I don't handle steps
            assert isinstance(idx, slice) and cast(slice, idx).step is None
            start = idx.start if idx.start is not None else 0
            stop = idx.stop if idx.stop is not None else len(self)
            for i in range(start, stop):
                self.x[self.i + i] = val


class comp_mixin(SizedIterable, Generic[T]):
    # Technically, T must be comparable, but I'm not sure
    # how I constrain int to be that...
    def __lt__(self, other: SizedIterable[T]):
        for a, b in zip(self, other):
            if a < b:
                return True
            if a > b:
                return False
        return len(self) < len(other)


# Frequently used subsequences... The inheritance pattern here
# reflects that a mutable version over a type should be castable
# to an immutable.
class substr(subseq[str],   comp_mixin[str]): ... # noqal
class isseq(subseq[int],    comp_mixin[int]): ... # noqal
class misseq(msubseq[int],  isseq):           ... # noqal
