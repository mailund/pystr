from __future__ import annotations
import typing
from .subseq import SubSeq

S = typing.TypeVar('S', bound="String")


class Alphabet:
    _map: dict[str, int]
    _revmap: dict[int, str]

    def __init__(self, reference: str) -> None:
        self._map = {
            a: i+1  # reserve space for sentinel
            for i, a in enumerate(sorted(set(reference)))
        }
        self._revmap = {
            i: a for a, i in self._map.items()
        }
        # sentinel
        self._map[chr(0)] = 0
        self._revmap[0] = "✶"  # just a symbol unlikely to be in the string

        # We save some space by packing strings into bytearrays,
        # but that means that we must fit the entire alphabet
        # into a byte (or do some other encoding that I do not
        # feel up to implementing right now).
        assert len(self._map) <= 256, \
            "Cannot handle alphabets we cannot fit into bytes"  # noqal: E501

    def __len__(self) -> int:
        return len(self._map)

    def map(self, x: typing.Iterable[str]) -> bytearray:
        return bytearray(self._map[a] for a in x)

    def revmap(self, x: int | typing.Iterable[int]) -> str:
        if isinstance(x, int):
            return self._revmap[x]
        else:
            return ''.join(self._revmap[i] for i in x)


class String(SubSeq[int]):
    alpha: Alphabet

    def __init__(self,
                 x: str,
                 alpha: typing.Optional[Alphabet] = None
                 ) -> None:

        # Handle the alphabet
        self.alpha = alpha or Alphabet(x)

        # Generate the underlying bytes.
        underlying = self.alpha.map(x)
        underlying.append(0)  # add sentinel

        # Use the underlying bytes as a Sequence[int]
        # that we hold as a subseq[int].
        super().__init__(underlying)

    def __str__(self) -> str:
        return self.alpha.revmap(self)

    def __repr__(self) -> str:  # pragma: no cover
        cls_name = self.__class__.__name__
        return f"{cls_name}('{self.alpha.revmap(self)}')"

    # Hooking into the subseq's slicing here to add the
    # alphabet to sub-strings.
    def init_slice(self: S, clone: S,
                   x: typing.Sequence[int], start: int, stop: int
                   ) -> None:
        super().init_slice(clone, x, start, stop)
        clone.alpha = self.alpha
