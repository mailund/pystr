from __future__ import annotations
from typing import Optional, Sequence, TypeVar
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

    def __len__(self) -> int:
        return len(self._map)

    def map(self, x: str) -> list[int]:
        return [self._map[a] for a in x]

    def revmap(self, x: Sequence[int]) -> str:
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

        if alpha is None:
            self.alpha = Alphabet(x, include_sentinel)
        else:
            if append_sentinel:
                assert 0 in self.alpha._revmap, \
                    "Alphabet must have sentinel for us to append it."
            self.alpha = alpha

        y = self.alpha.map(x)
        if append_sentinel:
            y.append(0)

        super().__init__(y)

    def __str__(self) -> str:
        return self.alpha.revmap(self)

    # Hooking into the subseq's slicing here to add the
    # alphabet to sub-strings.
    def init_clone(self: S, clone: S,
                   x: Sequence[int], start: int, stop: int
                   ) -> None:
        super().init_clone(clone, x, start, stop)
        clone.alpha = self.alpha
