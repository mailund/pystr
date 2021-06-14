import typing
import itertools

from .subseq import SubSeq, MSubSeq
from .bv import BitVector
from .alphabet import Alphabet

T = typing.TypeVar('T')
UNDEFINED = -1  # Undefined val in SA


def classify_SL(is_S: BitVector, x: SubSeq[int]) -> None:
    last = len(x) - 1
    is_S[last] = True
    for i in reversed(range(last)):
        is_S[i] = x[i] < x[i+1] or (x[i] == x[i+1] and is_S[i+1])


def is_LMS(is_S: BitVector, i: int) -> bool:
    return is_S[i] and not is_S[i - 1] if i > 0 else False


class Buckets:
    buckets: list[int]

    def __init__(self, x: SubSeq[int], asize: int):
        self.buckets = [0] * asize
        for a in x:
            self.buckets[a] += 1

    def calc_fronts(self) -> typing.Callable[[int], int]:
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
        ends = [0] * len(self.buckets)
        s = 0
        for i, b in enumerate(self.buckets):
            s += b
            ends[i] = s

        def next_bucket(bucket: int) -> int:
            ends[bucket] -= 1
            return ends[bucket]

        return next_bucket


def bucket_LMS(x: SubSeq[int], sa: MSubSeq[int],
               buckets: Buckets, is_S: BitVector
               ) -> None:
    next_end = buckets.calc_ends()
    sa[:] = UNDEFINED
    for i in range(len(x)):
        if is_LMS(is_S, i):
            sa[next_end(x[i])] = i


def induce_L(x: SubSeq[int], sa: MSubSeq[int],
             buckets: Buckets, is_S: BitVector
             ) -> None:
    next_front = buckets.calc_fronts()
    for i in range(len(x)):
        j = sa[i] - 1
        if sa[i] == 0 or sa[i] == UNDEFINED:
            continue
        if is_S[j]:
            continue
        sa[next_front(x[j])] = j


def induce_S(x: SubSeq[int], sa: MSubSeq[int],
             buckets: Buckets, is_S: BitVector
             ) -> None:
    next_end = buckets.calc_ends()
    for i in reversed(range(len(x))):
        j = sa[i] - 1
        if sa[i] == 0:
            continue  # noqa: 701
        if not is_S[j]:
            continue  # noqa: 701
        sa[next_end(x[j])] = j


def equal_LMS(x: SubSeq[int], is_S: BitVector, i: int, j: int) -> bool:
    if i == j:
        # This happens as a special case in the beginning of placing them.
        return True

    for k in itertools.count():  # k goes from 0 to infinity
        iLMS = is_LMS(is_S, i + k)
        jLMS = is_LMS(is_S, j + k)
        if k > 0 and iLMS and jLMS:
            return True
        if iLMS != jLMS or x[i+k] != x[j+k]:
            return False

    # This assert is only hear to help the linter...
    # (checker doesn't understand infinite generators yet)
    assert False, "We only leave the loop with a return."  # pragma: no cover


def compact_seq(x: MSubSeq[T],
                p: typing.Callable[[T], bool],
                y: typing.Optional[typing.Iterable[T]] = None) -> int:
    """Compacts elements in y satisfying p into x.
If y is None, do it from x to x."""
    y = y if y is not None else x
    k = 0
    for i in y:
        if p(i):
            x[k] = i
            k += 1
    return k


def reduce_LMS(x: SubSeq[int], sa: MSubSeq[int], is_S: BitVector) \
        -> tuple[MSubSeq[int], MSubSeq[int], int]:
    # Compact all the LMS indices in the first
    # part of the suffix array...
    k = compact_seq(sa, lambda j: is_LMS(is_S, j))

    # Create the alphabet and write the translation
    # into the buffer in the right order
    compact, buffer = sa[:k], sa[k:]
    buffer[:] = UNDEFINED
    prev, letter = compact[0], 0
    for j in compact:
        if not equal_LMS(x, is_S, prev, j):
            letter += 1
        buffer[j//2] = letter
        prev = j

    # Then compact the buffer into the reduced string
    compact_seq(buffer, lambda i: i != UNDEFINED)

    return buffer[:k], compact, letter + 1


def reverse_reduction(x: SubSeq[int], sa: MSubSeq[int],
                      offsets: MSubSeq[int], red_sa: MSubSeq[int],
                      buckets: Buckets,
                      is_S: BitVector
                      ) -> None:

    # Work out where the LMS strings are in the
    # original string. Compact those indices
    # into the buffer offsets
    compact_seq(offsets, lambda i: is_LMS(is_S, i), range(len(x)))

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
             is_S: BitVector
             ) -> None:
    if len(x) == asize:
        # base case...
        for i, a in enumerate(x):
            sa[a] = i

    else:  # recursive case...
        classify_SL(is_S, x)
        buckets: Buckets = Buckets(x, asize)

        bucket_LMS(x, sa, buckets, is_S)
        induce_L(x, sa, buckets, is_S)
        induce_S(x, sa, buckets, is_S)

        red, red_sa, red_asize = reduce_LMS(x, sa, is_S)

        del buckets  # Save memory in the recursive call
        sais_rec(red, red_sa, red_asize, is_S)
        # restore state...
        classify_SL(is_S, x)
        buckets = Buckets(x, asize)

        reverse_reduction(x, sa, red, red_sa, buckets, is_S)
        induce_L(x, sa, buckets, is_S)
        induce_S(x, sa, buckets, is_S)


def sais_alphabet(x: SubSeq[int], alpha: Alphabet) -> list[int]:
    sa = [0] * len(x)
    is_S = BitVector(size=len(x))
    sais_rec(x, MSubSeq[int](sa), len(alpha), is_S)
    return sa


def sais(x: str) -> list[int]:
    x_, alpha = Alphabet.mapped_subseq_with_sentinel(x)
    return sais_alphabet(x_, alpha)
