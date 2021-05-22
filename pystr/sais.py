from typing import cast, Optional, Iterable, Callable, TypeVar
from itertools import count
from .subseq import isseq, imseq, mutsubseq
from .bv import BitVector


T = TypeVar('T')
UNDEFINED = -1  # Undefined val in SA


def map_string(x: str) -> tuple[isseq, int]:
    # Get a set of the letters in x and number them (+1 for sentinel)
    alphabet = {
        a: i + 1 for i, a in enumerate(sorted(set(x)))
    }

    # Build a string and add the sentinel
    new_string = list(alphabet[a] for a in x)
    new_string.append(0)  # add sentinel

    return isseq(new_string), len(alphabet) + 1


def classify_SL(is_S: BitVector, x: isseq) -> None:
    last = len(x) - 1
    is_S[last] = True
    for i in reversed(range(last)):
        is_S[i] = x[i] < x[i+1] or (x[i] == x[i+1] and is_S[i+1])


def is_LMS(is_S: BitVector, i: int) -> bool:
    return False if i == 0 else is_S[i] and not is_S[i - 1]


class Buckets:
    buckets: list[int]
    fronts: list[int]

    def __init__(self, x: isseq, asize: int):
        self.buckets = [0] * asize
        self.fronts = [0] * asize
        for a in x:
            self.buckets[a] += 1

    def calc_fronts(self):
        s = 0
        for i, b in enumerate(self.buckets):
            self.fronts[i] = s
            s += b

    def calc_ends(self):
        s = 0
        for i, b in enumerate(self.buckets):
            s += b
            self.fronts[i] = s

    def insert_front(self, out: imseq, bucket: int, val: int):
        out[self.fronts[bucket]] = val
        self.fronts[bucket] += 1

    def insert_end(self, out: imseq, bucket: int, val: int):
        self.fronts[bucket] -= 1
        out[self.fronts[bucket]] = val


def bucket_LMS(x: isseq, sa: imseq, buckets: Buckets, is_S: BitVector):
    buckets.calc_ends()
    sa[:] = UNDEFINED
    for i in range(len(x)):
        if is_LMS(is_S, i):
            buckets.insert_end(sa, x[i], i)


def induce_L(x: isseq, sa: imseq, buckets: Buckets, is_S: BitVector):
    buckets.calc_fronts()
    for i in range(len(x)):
        j = sa[i] - 1
        if sa[i] == 0 or sa[i] == UNDEFINED: continue # noqa: 701
        if is_S[j]:                          continue # noqa: 701
        buckets.insert_front(sa, x[j], j)


def induce_S(x: isseq, sa: imseq, buckets: Buckets, is_S: BitVector):
    buckets.calc_ends()
    for i in reversed(range(len(x))):
        j = sa[i] - 1
        if sa[i] == 0:  continue # noqa: 701
        if not is_S[j]: continue # noqa: 701
        buckets.insert_end(sa, x[j], j)


def equal_LMS(x: isseq, is_S: BitVector, i: int, j: int) -> bool:
    if i == j:                      return True   # noqa: 701
    if i == len(x) or j == len(x):  return False  # noqa: 701

    for k in count():
        iLMS = is_LMS(is_S, i + k)
        jLMS = is_LMS(is_S, j + k)
        if k > 0 and iLMS and jLMS:
            return True
        if iLMS != jLMS or x[i+k] != x[j+k]:
            return False

    # This assert is only hear to help the linter...
    # It doesn't understand that count() never terminates
    assert False, "We only leave the loop with a return."


# FIXME: this probably should go to a helper file...
def compact_seq(x: mutsubseq[T], p: Callable[[T], bool],
                y: Optional[Iterable[T]] = None) -> int:
    """Compacts elements in y satisfying p into x.
If y is None, do it from x to x."""
    y = y if y is not None else x
    k = 0
    for i in y:
        if p(i):
            x[k] = i
            k += 1
    return k


def reduce_LMS(x: isseq, sa: imseq, is_S: BitVector) \
        -> tuple[imseq, imseq, int]:
    # Compact all the LMS indices in the first
    # part of the suffix array...
    k = compact_seq(sa, lambda i: is_LMS(is_S, i))

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


def reverse_reduction(x: isseq, sa: imseq,
                      offsets: imseq, red_sa: imseq,
                      buckets: Buckets,
                      is_S: BitVector):

    # Work out where the LMS strings are in the
    # original string. Compact those indices
    # into the buffer offsets
    compact_seq(offsets, lambda i: is_LMS(is_S, i), range(len(x)))

    # Compact the original indices into sa
    for i, j in enumerate(red_sa):
        sa[i] = offsets[j]

    # Mark the sa after the LMS indices as undefined
    sa[len(red_sa):] = UNDEFINED

    buckets.calc_ends()
    for i in reversed(range(len(red_sa))):
        j, red_sa[i] = red_sa[i], UNDEFINED
        buckets.insert_end(sa, x[j], j)


def sais_rec(x: isseq, sa: imseq, asize: int, is_S: BitVector):
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
        sais_rec(cast(isseq, red), red_sa, red_asize, is_S)
        # restore state...
        classify_SL(is_S, x)
        buckets = Buckets(x, asize)

        reverse_reduction(x, sa, red, red_sa, buckets, is_S)
        induce_L(x, sa, buckets, is_S)
        induce_S(x, sa, buckets, is_S)


def sais(x: str) -> list[int]:
    s, asize = map_string(x)
    sa = [0] * len(s)
    is_S = BitVector(size=len(s))
    sais_rec(s, imseq(sa), asize, is_S)
    return sa[1:]
