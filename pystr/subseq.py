from __future__ import annotations
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Protocol, Generic, TypeVar, Optional, Sized
from typing import overload, cast

# Type specifications...
T = TypeVar('T')
S = TypeVar('S', covariant=True)
R = TypeVar('R', contravariant=True)


class Subable(Protocol[S]):
    def __len__(self) -> int: ...
    @overload
    def __getitem__(self, i: int) -> S: ...
    @overload
    def __getitem__(self, i: slice) -> Subable[S]: ...


class MutSubable(Subable, Protocol[R]):
    def __setitem__(self, i: int, val: R): ...


class SizedIterable(Sized, Iterable[T]):
    ...


# Then the functional stuff...
class base_ops_mixin(Generic[T]):
    x: Subable[T]
    i: int
    j: int

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


class init_check_mixin(Generic[T]):
    x: Subable[T]
    i: int
    j: int

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
            "Slices must be within the sequence's range."
        assert 0 <= self.j <= len(self.x), \
            "Slices must be within the sequence's range."


class get_mixin(Generic[T]):
    x: Subable[T]
    i: int
    j: int

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


class set_mixin(Generic[T]):
    x: Subable[T]  # Is a MutSubable, but we need this for type checker
    i: int
    j: int

    # This is just for the type system... it wants a len() method.
    # If you put base_ops_mixin before set_mixin in the classes,
    # you will never see this one
    def __len__(self):
        return super().__len__()

    # FIXME: I haven't handled if the right-hand-side isn't a scalar
    def __setitem__(self, idx: int | slice, val: T):
        # FIXME: The casts are only here because the type-checker is
        # incredibly stupid. There are ways around it, when I get the time
        if type(idx) == int:
            cast(MutSubable[T], self.x)[self.i + cast(int, idx)] = val
        else:
            # I don't handle steps
            assert type(idx) == slice and cast(slice, idx).step is None
            start = cast(slice, idx).start \
                if cast(slice, idx).start is not None else 0
            stop = cast(slice, idx).stop \
                if cast(slice, idx).stop is not None else len(self)
            for i in range(start, stop):
                cast(MutSubable[T], self.x)[self.i + i] = val


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


# Making the classes concrete...
@dataclass(frozen=True, eq=False)
class subseq(init_check_mixin[T], base_ops_mixin[T], get_mixin[T]):
    """This is a wrapper around lists and strings that lets us slice them
without copying them.
"""
    x: Subable[T]  # Maybe separate mutable/immutable ?
    i: int = 0
    j: int = -1

    # These are needed to inform the type checker about the
    # two different return types for indexing/slicing.
    @overload
    def __getitem__(self, _: int) -> T: ...
    @overload
    def __getitem__(self, _: slice) -> subseq[T]: ...
    # The type checker wants an implementation...
    def __getitem__(self, idx): ...
    del __getitem__  # but we remove it again (we just wanted the type hints)


@dataclass(frozen=True, eq=False)
class mutsubseq(init_check_mixin[T], base_ops_mixin[T],
                get_mixin[T], set_mixin[T]):
    x: MutSubable[T]
    i: int = 0
    j: int = -1

    # These are needed to inform the type checker about the
    # two different return types for indexing/slicing.
    @overload
    def __getitem__(self, _: int) -> T: ...
    @overload
    def __getitem__(self, _: slice) -> mutsubseq[T]: ...

    # The type checker demands an implementation...
    def __getitem__(self, idx): ...
    del __getitem__  # ...but I just want the inherited one


# Frequently used subsequences... Unfortunately, I need the overloading
# to make the type checker understand that we always get the same class
# back when we index on a slice, and I cannot automatically generate them
# since the type checker is static... so I have to repeat the same
# code for that.
class substr(subseq[str], comp_mixin[str]):
    @overload
    def __getitem__(self, _: int) -> str: ...
    @overload
    def __getitem__(self, _: slice) -> substr: ...
    # The type checker demands an implementation...
    def __getitem__(self, _): ...
    del __getitem__  # ...but I just want the inherited one


class isseq(subseq[int], comp_mixin[int]):
    @overload
    def __getitem__(self, _: int) -> int: ...
    @overload
    def __getitem__(self, _: slice) -> isseq: ...
    # The type checker demands an implementation...
    def __getitem__(self, _): ...
    del __getitem__  # ...but I just want the inherited one


class imseq(mutsubseq[int], comp_mixin[int]):
    @overload
    def __getitem__(self, _: int) -> int: ...
    @overload
    def __getitem__(self, _: slice) -> imseq: ...
    # The type checker demands an implementation...
    def __getitem__(self, _): ...
    del __getitem__  # ...but I just want the inherited one
