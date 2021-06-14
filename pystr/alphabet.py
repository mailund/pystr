from __future__ import annotations
import typing

from .subseq import SubSeq


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
        self._revmap[0] = "𝕊"  # just a symbol unlikely to be in the string

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

    def map_with_sentinel(self, x: typing.Iterable[str]) -> bytearray:
        b = self.map(x)
        b.append(0)
        return b

    def revmap(self, x: int | typing.Iterable[int]) -> str:
        if isinstance(x, int):
            return self._revmap[x]
        else:
            return ''.join(self._revmap[i] for i in x)

    @staticmethod
    def mapped_string(x: str) -> tuple[bytearray, Alphabet]:
        alpha = Alphabet(x)
        return alpha.map(x), alpha

    @staticmethod
    def mapped_subseq(x: str) -> tuple[SubSeq[int], Alphabet]:
        x_, alpha = Alphabet.mapped_string(x)
        return SubSeq[int](x_), alpha

    @staticmethod
    def mapped_string_with_sentinel(
        x: str
    ) -> tuple[bytearray, Alphabet]:
        alpha = Alphabet(x)
        return alpha.map_with_sentinel(x), alpha

    @staticmethod
    def mapped_subseq_with_sentinel(x: str) -> tuple[SubSeq[int], Alphabet]:
        x_, alpha = Alphabet.mapped_string_with_sentinel(x)
        return SubSeq[int](x_), alpha
