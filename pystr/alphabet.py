from __future__ import annotations
from typing import Optional, Sequence, Iterable, TypeVar
from .subseq import subseq

S = TypeVar('S', bound="String")


class Alphabet:
    _map: dict[str, int]
    _revmap: dict[int, str]

    def __init__(self, reference: str,
                 include_sentinel: bool = False) -> None:
        self._map = {
            a: i+include_sentinel
            for i, a in enumerate(sorted(set(reference)))
        }
        self._revmap = {
            i: a for a, i in self._map.items()
        }
        if include_sentinel:
            self._map[chr(0)] = 0
            self._revmap[0] = chr(0)

        # We save some space by packing strings into bytearrays,
        # but that means that we must fit the entire alphabet
        # into a byte (or do some other encoding that I do not
        # feel up to implementing right now).
        assert len(self._map) <= 256, \
            "Cannot handle alphabets we cannot fit into bytes"  # noqal: E501

    def __len__(self) -> int:
        return len(self._map)

    def map(self, x: Iterable[str]) -> bytearray:
        return bytearray(self._map[a] for a in x)

    def revmap(self, x: Iterable[int]) -> str:
        return ''.join(self._revmap[i] for i in x)


class String(subseq[int]):
    alpha: Alphabet

    def __init__(self,
                 x: str,
                 alpha: Optional[Alphabet] = None,
                 include_sentinel: bool = False,
                 append_sentinel: bool = False
                 ) -> None:

        # If we append the sentinel character, then
        # the alphabet must also have it
        include_sentinel |= append_sentinel

        # Handle the alphabet
        if alpha is None:
            self.alpha = Alphabet(x, include_sentinel)
        else:
            if append_sentinel:
                assert 0 in self.alpha._revmap, \
                    "Alphabet must have sentinel for us to append it."
            self.alpha = alpha

        # Generate the underlying bytes.
        underlying = self.alpha.map(x)
        if append_sentinel:
            underlying.append(0)

        # Use the underlying bytes as a Sequence[int]
        # that we hold as a subseq[int].
        super().__init__(underlying)

    def __str__(self) -> str:
        return self.alpha.revmap(self)

    # Hooking into the subseq's slicing here to add the
    # alphabet to sub-strings.
    def init_clone(self: S, clone: S,
                   x: Sequence[int], start: int, stop: int
                   ) -> None:
        super().init_clone(clone, x, start, stop)
        clone.alpha = self.alpha
