"""Implementation of the SAIS algorithm."""

import typing
import itertools

from .subseq import SubSeq, MSubSeq
from .bv import BitVector
from .alphabet import Alphabet

T = typing.TypeVar('T')
UNDEFINED = -1  # Undefined val in SA


def classify_sl(is_s: BitVector, x: SubSeq[int]) -> None:
    """Classify positions into S or L."""
    last = len(x) - 1
    is_s[last] = True
    for i in reversed(range(last)):
        is_s[i] = x[i] < x[i+1] or (x[i] == x[i+1] and is_s[i+1])


def is_lms(is_s: BitVector, i: int) -> bool:
    """Test if index i is an LMS index."""
    return is_s[i] and not is_s[i - 1] if i > 0 else False


class Buckets:
    """Buckets for bucketing suffixes."""

    buckets: list[int]

    def __init__(self, x: SubSeq[int], asize: int):
        """Compute the buckets from a string x over alphabet of size asize."""
        self.buckets = [0] * asize
        for a in x:
            self.buckets[a] += 1

    def calc_fronts(self) -> typing.Callable[[int], int]:
        """
        Get the front of the buckets.

        The result is a function for updating the buckets and
        returning the next available position in the bucket.
        """
        fronts = [0] * len(self.buckets)
        s = 0
        for i, b in enumerate(self.buckets):
            fronts[i] = s
            s += b

        def next_bucket(bucket: int) -> int:
            fronts[bucket] += 1
            return fronts[bucket] - 1

        return next_bucket

    def calc_ends(self) -> typing.Callable[[int], int]:
        """
        Get the end of the buckets.

        The result is a function for updating the buckets and
        returning the next available position in the bucket.
        """
        ends = [0] * len(self.buckets)
        s = 0
        for i, b in enumerate(self.buckets):
            s += b
            ends[i] = s

        def next_bucket(bucket: int) -> int:
            ends[bucket] -= 1
            return ends[bucket]

        return next_bucket


def bucket_lms(x: SubSeq[int], sa: MSubSeq[int],
               buckets: Buckets, is_s: BitVector
               ) -> None:
    """Place LMS strings in their correct buckets."""
    next_end = buckets.calc_ends()
    sa[:] = UNDEFINED
    for i, _ in enumerate(x):
        if is_lms(is_s, i):
            sa[next_end(x[i])] = i


def induce_l(x: SubSeq[int], sa: MSubSeq[int],
             buckets: Buckets, is_s: BitVector
             ) -> None:
    """Induce L suffixes from the LMS strings."""
    next_front = buckets.calc_fronts()
    for i in range(len(x)):
        j = sa[i] - 1
        if sa[i] == 0 or sa[i] == UNDEFINED:
            continue
        if is_s[j]:
            continue
        sa[next_front(x[j])] = j


def induce_s(x: SubSeq[int], sa: MSubSeq[int],
             buckets: Buckets, is_s: BitVector
             ) -> None:
    """Induce S suffixes from the L suffixes."""
    next_end = buckets.calc_ends()
    for i in reversed(range(len(x))):
        j = sa[i] - 1
        if sa[i] == 0:
            continue  # noqa: 701
        if not is_s[j]:
            continue  # noqa: 701
        sa[next_end(x[j])] = j


def equal_lms(x: SubSeq[int], is_s: BitVector, i: int, j: int) -> bool:
    """Test if two LMS strings are identical."""
    if i == j:
        # This happens as a special case in the beginning of placing them.
        return True

    for k in itertools.count():  # k goes from 0 to infinity
        i_lms = is_lms(is_s, i + k)
        j_lms = is_lms(is_s, j + k)
        if k > 0 and i_lms and j_lms:
            return True
        if i_lms != j_lms or x[i+k] != x[j+k]:
            return False

    # This assert is only hear to help the linter...
    # (checker doesn't understand infinite generators yet)
    assert False, "We only leave the loop with a return."  # pragma: no cover
    return False  # just for the linter


def compact_seq(x: MSubSeq[T],
                p: typing.Callable[[T], bool],
                y: typing.Optional[typing.Iterable[T]] = None) -> int:
    """
    Compacts elements in y satisfying p into x.

    If y is None, do it from x to x.
    """
    y = y if y is not None else x
    k = 0
    for i in y:
        if p(i):
            x[k] = i
            k += 1
    return k


def reduce_lms(x: SubSeq[int], sa: MSubSeq[int], is_s: BitVector) \
        -> tuple[MSubSeq[int], MSubSeq[int], int]:
    """Construct reduced string from LMS strings."""
    # Compact all the LMS indices in the first
    # part of the suffix array...
    k = compact_seq(sa, lambda j: is_lms(is_s, j))

    # Create the alphabet and write the translation
    # into the buffer in the right order
    compact, buffer = sa[:k], sa[k:]
    buffer[:] = UNDEFINED
    prev, letter = compact[0], 0
    for j in compact:
        if not equal_lms(x, is_s, prev, j):
            letter += 1
        buffer[j//2] = letter
        prev = j

    # Then compact the buffer into the reduced string
    compact_seq(buffer, lambda i: i != UNDEFINED)

    return buffer[:k], compact, letter + 1


def reverse_reduction(x: SubSeq[int], sa: MSubSeq[int],
                      offsets: MSubSeq[int], red_sa: MSubSeq[int],
                      buckets: Buckets,
                      is_s: BitVector
                      ) -> None:
    """Get the LMS string order back from the reduced suffix array."""
    # Work out where the LMS strings are in the
    # original string. Compact those indices
    # into the buffer offsets
    compact_seq(offsets, lambda i: is_lms(is_s, i), range(len(x)))

    # Compact the original indices into sa
    for i, j in enumerate(red_sa):
        sa[i] = offsets[j]

    # Mark the sa after the LMS indices as undefined
    sa[len(red_sa):] = UNDEFINED

    next_end = buckets.calc_ends()
    for i in reversed(range(len(red_sa))):
        j, red_sa[i] = red_sa[i], UNDEFINED
        sa[next_end(x[j])] = j


def sais_rec(x: SubSeq[int],
             sa: MSubSeq[int],
             asize: int,
             is_s: BitVector
             ) -> None:
    """Recursive SAIS algorithm."""
    if len(x) == asize:
        # base case...
        for i, a in enumerate(x):
            sa[a] = i

    else:  # recursive case...
        classify_sl(is_s, x)
        buckets: Buckets = Buckets(x, asize)

        bucket_lms(x, sa, buckets, is_s)
        induce_l(x, sa, buckets, is_s)
        induce_s(x, sa, buckets, is_s)

        red, red_sa, red_asize = reduce_lms(x, sa, is_s)

        del buckets  # Save memory in the recursive call
        sais_rec(red, red_sa, red_asize, is_s)
        # restore state...
        classify_sl(is_s, x)
        buckets = Buckets(x, asize)

        reverse_reduction(x, sa, red, red_sa, buckets, is_s)
        induce_l(x, sa, buckets, is_s)
        induce_s(x, sa, buckets, is_s)


def sais_alphabet(x: SubSeq[int], alpha: Alphabet) -> list[int]:
    """Run the sais algorithm from a subsequence and an alphabet."""
    sa = [0] * len(x)
    is_s = BitVector(size=len(x))
    sais_rec(x, MSubSeq[int](sa), len(alpha), is_s)
    return sa


def sais(x: str) -> list[int]:
    """Run the sais algorithm from a string."""
    x_, alpha = Alphabet.mapped_subseq_with_sentinel(x)
    return sais_alphabet(x_, alpha)
