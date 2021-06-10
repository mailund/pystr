import typing

from .alphabet import String
from .sais import sais_string  # For the search function

SENTINEL = 0


class CTable:
    _cumsum: list[int]

    def __init__(self, x: String):
        # Count occurrences of characters in x
        counts = [0] * len(x.alpha)
        for a in x:
            counts[a] += 1
        # Get the cumulative sum
        n = 0
        for a, count in enumerate(counts):
            counts[a] = n
            n += count
        # That is all we need...
        self._cumsum = counts

    def __str__(self) -> str:  # pragma: no cover
        return f"CTable[{self._cumsum}]"

    def __getitem__(self, a: int) -> int:
        return self._cumsum[a]


def bwt(x: String, sa: list[int], i: int) -> int:
    return SENTINEL if sa[i] == 0 else x[sa[i] - 1]


class OTable:
    _tbl: list[list[int]]

    def __init__(self, x: String, sa: list[int]) -> None:
        # We exclude $ from lookups, so there are this manh
        # rows.
        nrow = len(x.alpha) - 1
        # We need to index to len(x), but we don't represent first column
        # so there are len(x) columns.
        ncol = len(x)

        self._tbl = [[0] * ncol for _ in range(nrow)]

        # The first column is all zeros, the second
        # should hold a 1 in the row that has character
        # bwt[0]. The we b-1 because of the sentinel and
        # we use column 0 for the first real column.
        b = bwt(x, sa, 0)
        self._tbl[b-1][0] = 1

        # We already have cols 0 and 1. Now we need to
        # go up to (and including) len(x).
        for i in range(2, len(x)+1):
            b = bwt(x, sa, i-1)
            # Characters, except for sentinel
            for a in range(1, len(x.alpha)):
                self._tbl[a-1][i-1] = self._tbl[a-1][i-2] + (a == b)

    def __getitem__(self, idx: tuple[int, int]) -> int:
        a, i = idx
        assert a > 0, "Don't look up the sentinel"
        if i == 0:
            return 0  # column 0 is contant zero
        else:
            return self._tbl[a-1][i-1]


def preprocess(
    x_: str
) -> typing.Callable[[str], typing.Iterator[int]]:

    x = String(x_)
    sa = sais_string(x)
    ctab = CTable(x)
    otab = OTable(x, sa)

    def search(p_: str) -> typing.Iterator[int]:
        try:
            # Just use the alphabet's map. We don't
            # want the sentinel appended to p, and
            # we don't need to drag its alphabet around
            p = x.alpha.map(p_)
        except KeyError:
            return  # can't map, so no matches

        # Find interval of matches...
        L = 0       # Starting at 0 (the sentinel) handles empty strings
        R = len(x)  # len(x) include sentinel
        for a in reversed(p):
            L = ctab[a] + otab[a, L]
            R = ctab[a] + otab[a, R]
            if L >= R:
                return  # no matches

        # Report the matches
        for i in range(L, R):
            yield sa[i]

    return search
