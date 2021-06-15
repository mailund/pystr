import typing

from .subseq import SubSeq
from .alphabet import Alphabet
from .sais import sais_alphabet


def burrows_wheeler_transform_bytes(
    x: bytearray, alpha: Alphabet
) -> tuple[bytearray, list[int]]:
    sa = sais_alphabet(SubSeq[int](x), alpha)
    bwt = bytearray(x[j - 1] for j in sa)
    return bwt, sa


def burrows_wheeler_transform(
    x: str
) -> tuple[bytearray, Alphabet, list[int]]:
    x_, alpha = Alphabet.mapped_string_with_sentinel(x)
    sa = sais_alphabet(SubSeq[int](x_), alpha)
    bwt = bytearray(x_[j - 1] for j in sa)
    return bwt, alpha, sa


def reverse_burrows_wheeler_transform(
    bwt: bytearray
) -> bytearray:
    asize = max(bwt) + 1
    ctab = CTable(bwt, asize)
    otab = OTable(bwt, asize)

    i, x = 0, bytearray(len(bwt))
    for j in reversed(range(len(x)-1)):
        a = x[j] = bwt[i]
        i = ctab[a] + otab[a, i]

    return x


class CTable:
    _cumsum: list[int]

    def __init__(self, bwt: bytearray, asize: int) -> None:
        # Count occurrences of characters in bwt
        counts = [0] * asize
        for a in bwt:
            counts[a] += 1
        # Get the cumulative sum
        n = 0
        for a, count in enumerate(counts):
            counts[a] = n
            n += count
        # That is all we need...
        self._cumsum = counts

    def __getitem__(self, a: int) -> int:
        return self._cumsum[a]


class OTable:
    _tbl: list[list[int]]

    def __init__(self, bwt: bytearray, asize: int) -> None:
        # We exclude $ from lookups, so there are this many
        # rows.
        nrow = asize - 1
        # We need to index to len(bwt), but we don't represent first column
        # so there are len(bwt) columns.
        ncol = len(bwt)

        self._tbl = [[0] * ncol for _ in range(nrow)]

        # The first column is all zeros, the second
        # should hold a 1 in the row that has character
        # bwt[0]. The we b-1 because of the sentinel and
        # we use column 0 for the first real column.
        self._tbl[bwt[0]-1][0] = 1

        # We already have cols 0 and 1. Now we need to
        # go up to (and including) len(bwt).
        for i in range(2, len(bwt)+1):
            b = bwt[i-1]
            # Characters, except for sentinel
            for a in range(1, asize):
                self._tbl[a-1][i-1] = self._tbl[a-1][i-2] + (a == b)

    def __getitem__(self, idx: tuple[int, int]) -> int:
        a, i = idx
        assert a > 0, "Don't look up the sentinel"
        return 0 if i == 0 else self._tbl[a-1][i-1]


def searcher_from_tables(
    alpha: Alphabet,
    sa: list[int],
    ctab: CTable,
    otab: OTable
) -> typing.Callable[[str], typing.Iterator[int]]:

    def search(p_: str) -> typing.Iterator[int]:
        try:
            p = alpha.map(p_)
        except KeyError:
            return  # can't map, so no matches

        # Find interval of matches...
        L, R = 0, len(sa)
        for a in reversed(p):
            L = ctab[a] + otab[a, L]
            R = ctab[a] + otab[a, R]
            if L >= R:
                return  # no matches

        # Report the matches
        for i in range(L, R):
            yield sa[i]

    return search


def preprocess(
    x: str
) -> typing.Callable[[str], typing.Iterator[int]]:
    bwt, alpha, sa = burrows_wheeler_transform(x)
    ctab = CTable(bwt, len(alpha))
    otab = OTable(bwt, len(alpha))
    return searcher_from_tables(alpha, sa, ctab, otab)
