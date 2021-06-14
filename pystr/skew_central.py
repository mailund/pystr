"""
Straightforward implementation of the skew/DC3 algorithm

    - https://www.cs.helsinki.fi/u/tpkarkka/publications/jacm05-revised.pdf

"""

import typing
from .alphabet import Alphabet
from .skew_common import SENTINEL, SkewTripletDict, \
    triplet, radix3, bucket_sort, merge


def collect_alphabet(x: typing.Sequence[int],
                     idx: list[int]
                     ) -> SkewTripletDict:
    "Map the triplets starting at idx to a new alphabet."
    # I'm using a dictionary for the alphabet, but you can build
    # it more efficiently by looking at the previous triplet in the
    # sorted SA12. It won't affect the asymptotic running time,
    # though.
    alpha: SkewTripletDict = {
        # The (central and terminal) sentinel.
        # We never use it, but it gives the alphabet
        # the right size.
        (0, 0, 0): 0,
    }
    for i in idx:
        trip = triplet(x, i)
        if trip not in alpha:
            alpha[trip] = len(alpha)
    return alpha


def build_u(x: typing.Sequence[int], alpha: SkewTripletDict) -> list[int]:
    "Construct u string, using 1 as central sentinel."
    # I'm putting class [1] first. Then the sentinel will fall on
    # m//2 where m is the length of u. If you put class [2] first,
    # it would go at (m-1)//2.
    return [*(alpha[triplet(x, i)] for i in range(1, len(x), 3)),
            SENTINEL,
            *(alpha[triplet(x, i)] for i in range(2, len(x), 3))]


def u_idx(i: int, m: int) -> int:
    "Map indices in u back to indices in the original string."
    return 1 + 3 * i if i < m else 2 + 3 * (i - m - 1)


def skew_rec(x: typing.Sequence[int], asize: int) -> list[int]:
    "Recursive skew SA construction algorithm."

    SA12 = [i for i in range(len(x)) if i % 3 != 0]
    SA12 = radix3(x, asize, SA12)
    new_alpha = collect_alphabet(x, SA12)

    # The alphabet includes sentinel, so it has to be
    # one larger than SA12 to have given all triplets
    # unique names... Thus the <= instead of <.
    if len(new_alpha) <= len(SA12):
        # Recursively sort SA12.
        # Construct the u string and compute its suffix array,
        # then map the suffix array back to SA12 indices
        u = build_u(x, new_alpha)
        sa_u = skew_rec(u, len(new_alpha))
        m = len(sa_u) // 2
        SA12 = [u_idx(i, m) for i in sa_u if i != m]

    # Special case if the last index is class 0. Then the
    # following class 1 isn't there, but we should treat it
    # as the smallest string in the class.
    SA3 = ([len(x) - 1] if len(x) % 3 == 1 else []) + \
        [i - 1 for i in SA12 if i % 3 == 1]
    SA3 = bucket_sort(x, asize, SA3)
    return merge(x, SA12, SA3)


def skew(x: str) -> list[int]:
    "Skew algorithm for a string."
    # When we use the central sentinel, we don't include the terminal
    # sentinel, so we don't use a String. We have to explicitly add
    # the first suffix, though, to match the interface of the other
    # constructions.
    x_, alpha = Alphabet.mapped_string(x)
    return [len(x_)] + skew_rec(x_, len(alpha))
