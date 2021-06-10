from __future__ import annotations
import typing


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
        self._revmap[0] = "◦"  # just a symbol unlikely to be in the string

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
