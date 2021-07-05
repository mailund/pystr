"""Implementatin of the Burrows-Wheeler transform and related algorithms."""

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


def burrows_wheeler_transform_bytes(x: bytearray,
                                    alpha: Alphabet) \
        -> tuple[bytearray, list[int]]:
    """
    Construct the Burrows-Wheeler transform.

    Build the bwt string from a mapped string x and the
    alphabet x was mapped to. Returns the transformed string
    and the suffix array over x.
    """
    sa = sais_alphabet(SubSeq[int](x), alpha)
    bwt = bytearray(x[j - 1] for j in sa)
    return bwt, sa


def burrows_wheeler_transform(x: str) -> tuple[bytearray, Alphabet, list[int]]:
    """
    Construct the Burrows-Wheeler transform.

    Build the bwt string from a string x, first mapping
    x to a new alphabet.

    Returns the transformed string, the mapping alphabet,
    and the suffix array over x.
    """
    x_, alpha = Alphabet.mapped_string_with_sentinel(x)
    sa = sais_alphabet(SubSeq[int](x_), alpha)
    bwt = bytearray(x_[j - 1] for j in sa)
    return bwt, alpha, sa


def reverse_burrows_wheeler_transform(bwt: bytearray) -> bytearray:
    """
    Reverse the Burrows-Wheeler transform.

    Given a Burrows-Wheeler transformed string, bwt,
    compute the original string and return it.
    """
    asize = max(bwt) + 1
    ctab = CTable(bwt, asize)
    otab = OTable(bwt, asize)

    i, x = 0, bytearray(len(bwt))
    for j in reversed(range(len(x)-1)):
        a = x[j] = bwt[i]
        i = ctab[a] + otab[a, i]

    return x


class CTable:
    """
    C-table for other bwt/fm-index search algorithms.

    for CTable ctab, ctab[⍺] is the number of occurrences
    of letters a < ⍺ in the bwt string (or the orignal string,
    since they have the same letters).
    """

    _cumsum: list[int]

    def __init__(self, bwt: bytearray, asize: int) -> None:
        """
        Construct a C-table.

        Compute the C-table from the bwt transformed string and
        the alphabet size.
        """
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
        """Get the number of occurrences of letters in the bwt less than a."""
        return self._cumsum[a]


class OTable:
    """
    O-table for the FM-index based search.

    For OTable otab, otab[a,i] is the number of occurrences j < i
    where bwt[j] == a.
    """

    _tbl: list[list[int]]

    def __init__(self, bwt: bytearray, asize: int) -> None:
        """
        Create O-table.

        Compute the O-table from the bwt transformed string and the size
        of the alphabet the bwt string is over.
        """
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
        """
        Get the number of occurrences j < i where bwt[j] == a.

        a is the first and i the second value in the idx tuple.
        """
        a, i = idx
        assert a > 0, "Don't look up the sentinel"
        return 0 if i == 0 else self._tbl[a-1][i-1]


def preprocess_exact(x: str) -> tuple[Alphabet, list[int], CTable, OTable]:
    """Preprocess tables for exact FM/bwt search."""
    bwt, alpha, sa = burrows_wheeler_transform(x)
    ctab = CTable(bwt, len(alpha))
    otab = OTable(bwt, len(alpha))
    return alpha, sa, ctab, otab


def preprocess_rotab(x: str) -> OTable:
    """Build reverse O-table for approximate searching."""
    bwt, alpha, _ = burrows_wheeler_transform(x[::-1])
    rotab = OTable(bwt, len(alpha))
    return rotab


def preprocess_approx(x: str
                      ) -> tuple[Alphabet, list[int], CTable, OTable, OTable]:
    """Preprocess tables for approximative bwa search."""
    exact = preprocess_exact(x)
    rotab = preprocess_rotab(x)
    return (*exact, rotab)


def exact_searcher_from_tables(
        alpha: Alphabet,
        sa: list[int],
        ctab: CTable,
        otab: OTable) -> ExactSearchFunc:
    """Build an exact search function from preprocessed tables."""

    def search(p_: str) -> typing.Iterator[int]:
        try:
            p = alpha.map(p_)
        except KeyError:
            return  # can't map, so no matches

        # Find interval of matches...
        left, right = 0, len(sa)
        for a in reversed(p):
            left = ctab[a] + otab[a, left]
            right = ctab[a] + otab[a, right]
            if left >= right:
                return  # no matches

        # Report the matches
        for i in range(left, right):
            yield sa[i]

    return search


def exact_preprocess(x: str) -> ExactSearchFunc:
    """Build an exact search function for searching in string x."""
    return exact_searcher_from_tables(*preprocess_exact(x))


BwtApproxTables = typing.NamedTuple(
    "BwtApproxTables",
    [("alpha", Alphabet), ("sa", list[int]),
     ("ctab", CTable), ("otab", OTable),
     ("rotab", OTable), ("dtab", list[int]),
     ("edit_ops", list[Edit]), ("p", bytearray)]
)


def do_m(tbls: BwtApproxTables,
         i: int, left: int, right: int,
         edits: int) -> typing.Iterator[tuple[int, str]]:
    """Perform a match/mismatch operation in the approx search."""
    tbls.edit_ops.append(Edit.Match)
    for a in range(1, len(tbls.alpha)):
        next_left = tbls.ctab[a] + tbls.otab[a, left]
        next_right = tbls.ctab[a] + tbls.otab[a, right]
        if next_left >= next_right:
            continue

        next_edits = edits-(a != tbls.p[i])
        yield from rec_search(tbls, i-1, next_left, next_right, next_edits)
    tbls.edit_ops.pop()


def do_i(tbls: BwtApproxTables,
         i: int, left: int, right: int,
         edits: int) -> typing.Iterator[tuple[int, str]]:
    """Perform an insertion operation in the approx search."""
    tbls.edit_ops.append(Edit.Insert)
    yield from rec_search(tbls, i - 1, left, right, edits - 1)
    tbls.edit_ops.pop()


def do_d(tbls: BwtApproxTables,
         i: int, left: int, right: int,
         edits: int) -> typing.Iterator[tuple[int, str]]:
    """Perform a deletion operation in the approx search."""
    tbls.edit_ops.append(Edit.Delete)
    for a in range(1, len(tbls.alpha)):
        next_left = tbls.ctab[a] + tbls.otab[a, left]
        next_right = tbls.ctab[a] + tbls.otab[a, right]
        if next_left >= next_right:
            continue
        yield from rec_search(tbls, i, next_left, next_right, edits-1)
    tbls.edit_ops.pop()


def rec_search(tbls: BwtApproxTables,
               i: int, left: int, right: int,
               edits: int) -> typing.Iterator[tuple[int, str]]:
    """Handle recursive operations in approx search."""
    # Do we have a match here?
    if i < 0 <= edits:
        # Remember to reverse the operations, since
        # we did the backwards in the bwt search
        cigar = edits_to_cigar(tbls.edit_ops[::-1])
        for j in range(left, right):
            yield tbls.sa[j], cigar
        return

        # Can we get to a match with the edits we have left?
    if edits < tbls.dtab[i]:
        return

    yield from do_m(tbls, i, left, right, edits)
    yield from do_i(tbls, i, left, right, edits)
    yield from do_d(tbls, i, left, right, edits)


def build_dtab(p: bytearray, sa: list[int],
               ctab: CTable, rotab: OTable) -> list[int]:
    """Build the D table for the approximative search."""
    dtab = [0] * len(p)
    min_edits = 0
    left, right, i = 0, len(sa), len(p) - 1
    for i, a in enumerate(p):
        left = ctab[a] + rotab[a, left]
        right = ctab[a] + rotab[a, right]
        if left == right:
            min_edits += 1
            left, right = 0, len(sa)
        dtab[i] = min_edits
    return dtab


def approx_searcher_from_tables(
        alpha: Alphabet,
        sa: list[int],
        ctab: CTable,
        otab: OTable,
        rotab: OTable) -> ApproxSearchFunc:
    """Build an exact search function from preprocessed tables."""

    def search(p_: str, edits: int) -> typing.Iterator[tuple[int, str]]:
        assert p_, "We can't do approx search with an empty pattern!"
        try:
            p = alpha.map(p_)
        except KeyError:
            return  # can't map, so no matches

        # Build D table for the read...
        dtab = [0] * len(p)
        min_edits = 0
        left, right, i = 0, len(sa), len(p) - 1
        for i, a in enumerate(p):
            left = ctab[a] + rotab[a, left]
            right = ctab[a] + rotab[a, right]
            if left == right:
                min_edits += 1
                left, right = 0, len(sa)
            dtab[i] = min_edits

        tbls = BwtApproxTables(alpha, sa,
                               ctab, otab, rotab, dtab,
                               list[Edit](), p)

        # Do the first operation in this function to avoid
        # deletions in the beginning (end) of the search
        left, right, i = 0, len(sa), len(p) - 1
        yield from do_m(tbls, i, left, right, edits)
        yield from do_i(tbls, i, left, right, edits)

    return search


def approx_preprocess(x: str) -> ApproxSearchFunc:
    """Build an approximative search function for searching in string x."""
    return approx_searcher_from_tables(*preprocess_approx(x))
