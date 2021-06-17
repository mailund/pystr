import typing

from .subseq import SubSeq
from .alphabet import Alphabet
from .sais import sais_alphabet
from .approx import Edit, edits_to_cigar

ExactSearchFunc = typing.Callable[
    [str],
    typing.Iterator[int]
]
ApproxSearchFunc = typing.Callable[
    [str,
     int],
    typing.Iterator[tuple[int, str]]
]


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


def preprocess_exact(x: str) -> tuple[Alphabet, list[int], CTable, OTable]:
    bwt, alpha, sa = burrows_wheeler_transform(x)
    ctab = CTable(bwt, len(alpha))
    otab = OTable(bwt, len(alpha))
    return alpha, sa, ctab, otab


def preprocess_rotab(x: str) -> OTable:
    bwt, alpha, _ = burrows_wheeler_transform(x[::-1])
    rotab = OTable(bwt, len(alpha))
    return rotab


def preprocess_approx(
    x: str
) -> tuple[Alphabet, list[int], CTable, OTable, OTable]:
    exact = preprocess_exact(x)
    rotab = preprocess_rotab(x)
    return (*exact, rotab)


def exact_searcher_from_tables(
        alpha: Alphabet,
        sa: list[int],
        ctab: CTable,
        otab: OTable) -> ExactSearchFunc:

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


def exact_preprocess(x: str) -> ExactSearchFunc:
    return exact_searcher_from_tables(*preprocess_exact(x))


def approx_searcher_from_tables(
        alpha: Alphabet,
        sa: list[int],
        ctab: CTable,
        otab: OTable,
        rotab: OTable) -> ApproxSearchFunc:

    edit_operations: list[Edit] = []

    def do_M(p: bytearray,
             i: int, L: int, R: int,
             edits: int, D: list[int]
             ) -> typing.Iterator[tuple[int, str]]:
        edit_operations.append(Edit.M)
        for a in range(1, len(alpha)):
            next_L = ctab[a] + otab[a, L]
            next_R = ctab[a] + otab[a, R]
            if next_L >= next_R:
                continue
            yield from rec_search(p, i-1, next_L, next_R, edits-(a != p[i]), D)
        edit_operations.pop()

    def do_I(p: bytearray,
             i: int, L: int, R: int,
             edits: int, D: list[int]
             ) -> typing.Iterator[tuple[int, str]]:
        edit_operations.append(Edit.I)
        yield from rec_search(p, i - 1, L, R, edits - 1, D)
        edit_operations.pop()

    def do_D(p: bytearray,
             i: int, L: int, R: int,
             edits: int, D: list[int]
             ) -> typing.Iterator[tuple[int, str]]:
        edit_operations.append(Edit.D)
        for a in range(1, len(alpha)):
            next_L = ctab[a] + otab[a, L]
            next_R = ctab[a] + otab[a, R]
            if next_L >= next_R:
                continue
            yield from rec_search(p, i, next_L, next_R, edits-1, D)
        edit_operations.pop()

    def rec_search(p: bytearray,
                   i: int, L: int, R: int,
                   edits: int, D: list[int]
                   ) -> typing.Iterator[tuple[int, str]]:

        # Do we have a match here?
        if i < 0 and edits >= 0:
            # Remember to reverse the operations, since
            # we did the backwards in the bwt search
            cigar = edits_to_cigar(edit_operations[::-1])
            for j in range(L, R):
                yield sa[j], cigar
            return

        # Can we get to a match with the edits we have left?
        if edits < D[i]:
            return

        yield from do_M(p, i, L, R, edits, D)
        yield from do_I(p, i, L, R, edits, D)
        yield from do_D(p, i, L, R, edits, D)

    def search(p_: str, edits: int) -> typing.Iterator[tuple[int, str]]:
        assert p_, "We can't do approx search with an empty pattern!"
        try:
            p = alpha.map(p_)
        except KeyError:
            return  # can't map, so no matches

        # Build D table for the read...
        D = [0] * len(p)
        min_edits = 0
        L, R, i = 0, len(sa), len(p) - 1
        for i, a in enumerate(p):
            L = ctab[a] + rotab[a, L]
            R = ctab[a] + rotab[a, R]
            if L == R:
                min_edits += 1
                L, R = 0, len(sa)
            D[i] = min_edits

        # Do the first operation in this function to avoid
        # deletions in the beginning (end) of the search
        L, R, i = 0, len(sa), len(p) - 1
        yield from do_M(p, i, L, R, edits, D)
        yield from do_I(p, i, L, R, edits, D)

    return search


def approx_preprocess(x: str) -> ApproxSearchFunc:
    return approx_searcher_from_tables(*preprocess_approx(x))
