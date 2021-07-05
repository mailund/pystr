"""Implements code for mapping strings to smaller alphabets."""

from __future__ import annotations
import typing

from .subseq import SubSeq


class Alphabet:
    """Handles mapping from strings to smaller alphabets."""

    _map: dict[str, int]
    _revmap: dict[int, str]

    def __init__(self, reference: str) -> None:
        """
        Create an alphabet with the letters found in reference.

        An alphabet always has a sentinel symbol, byte zero, regardless of
        whether it is found in reference.
        """
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
        """Return the number of letters in the alphabet."""
        return len(self._map)

    def map(self, x: typing.Iterable[str]) -> bytearray:
        """
        Map the characters in x to their corresponding letters in the alphabet.

        The result is returned as a bytearray. If x contains a letter not in
        the alphabet, map raises a KeyError.
        """
        return bytearray(self._map[a] for a in x)

    def map_with_sentinel(self, x: typing.Iterable[str]) -> bytearray:
        """
        Map x to the bytes in the alphabet.

        Maps the characters in x to their corresponding letters in the
        alphabet and returns the result as a bytearray. If x contains a
        letter not in the alphabet, map raises a KeyError.
        The result has the sentinel added to it,
        so the last character in the result is the zero byte.
        """
        b = self.map(x)
        b.append(0)
        return b

    def revmap(self, x: int | typing.Iterable[int]) -> str:
        """
        Map from alphabet to original alphabet.

        Maps a character from the alphabet back to the corresponding
        character in the reference used to create the alphabet.
        """
        if isinstance(x, int):
            return self._revmap[x]
        return ''.join(self._revmap[i] for i in x)

    @staticmethod
    def mapped_string(x: str) -> tuple[bytearray, Alphabet]:
        """
        Create mapped string with corresponding alphabet.

        Creates an alphabet from x, maps x to theh alphabet,
        then returns the mapped string and the alphabet.
        """
        alpha = Alphabet(x)
        return alpha.map(x), alpha

    @staticmethod
    def mapped_subseq(x: str) -> tuple[SubSeq[int], Alphabet]:
        """
        Create mapped string with corresponding alphabet.

        Creates an alphabet from x, maps x to theh alphabet,
        then returns the mapped string and the alphabet.
        The resulting string is a SubSeq[int], unlike mapped_string(x) which
        returns a bytearray for the mapped string.
        """
        x_, alpha = Alphabet.mapped_string(x)
        return SubSeq[int](x_), alpha

    @staticmethod
    def mapped_string_with_sentinel(x: str) -> tuple[bytearray, Alphabet]:
        """
        Create mapped string with corresponding alphabet.

        Creates an alphabet from x, maps x to theh alphabet,
        then returns the mapped string and the alphabet.
        The mapped string is terminated by the sentinel (zero) byte.
        """
        alpha = Alphabet(x)
        return alpha.map_with_sentinel(x), alpha

    @staticmethod
    def mapped_subseq_with_sentinel(x: str) -> tuple[SubSeq[int], Alphabet]:
        """
        Create mapped string with corresponding alphabet.

        Creates an alphabet from x, maps x to theh alphabet,
        then returns the mapped string and the alphabet.
        The mapped string is terminated by the sentinel (zero) byte.
        The resulting string is a SubSeq[int], unlike
        mapped_string_with_sentinel(x) which
        returns a bytearray for the mapped string.
        """
        x_, alpha = Alphabet.mapped_string_with_sentinel(x)
        return SubSeq[int](x_), alpha
