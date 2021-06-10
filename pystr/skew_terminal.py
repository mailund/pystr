"""
Straightforward implementation of the skew/DC3 algorithm

    - https://www.cs.helsinki.fi/u/tpkarkka/publications/jacm05-revised.pdf

"""

import typing

from .alphabet_string import String
from .skew_common import SkewTripletDict, \
    triplet, radix3, bucket_sort, merge


def collect_alphabet(x: typing.Sequence[int],
                     idx: list[int]
                     ) -> SkewTripletDict:
    "Map the triplets starting at idx to a new alphabet."
    # When we start with a terminal sentinel, we don't need to
    # explicitly add the central one, so we don't...
    alpha: SkewTripletDict = {}
    for i in idx:
        trip = triplet(x, i)
        if trip not in alpha:
            alpha[trip] = len(alpha)
    return alpha


def build_u(x: typing.Sequence[int], alpha: SkewTripletDict) -> list[int]:
    "Construct u string, using 1 as central sentinel."
    # I'm putting class [1] first. Then will end at (m+1)//2
    # where m is the length of u.
    return [*(alpha[triplet(x, i)] for i in range(1, len(x), 3)),
            # No central sentinel in this version
            *(alpha[triplet(x, i)] for i in range(2, len(x), 3))]


def u_idx(i: int, m: int) -> int:
    "Map indices in u back to indices in the original string."
    # The mapping for i >= m is different when we don't have the
    # central terminal
    return 1 + 3 * i if i < m else 2 + 3 * (i - m)


def skew_rec(x: typing.Sequence[int], asize: int) -> list[int]:
    "Recursive skew SA construction algorithm."

    SA12 = [i for i in range(len(x)) if i % 3 != 0]
    SA12 = radix3(x, asize, SA12)
    new_alpha = collect_alphabet(x, SA12)

    # Now both strings and alphabets only have implicit
    # sentinels, so the <= from central is now <
    if len(new_alpha) < len(SA12):
        # Recursively sort SA12.
        # Construct the u string and compute its suffix array,
        # then map the suffix array back to SA12 indices
        u = build_u(x, new_alpha)
        sa_u = skew_rec(u, len(new_alpha))
        # there's a plus one now for m, because we don't have the
        # central sentinel
        m = (len(sa_u)+1) // 2
        SA12 = [u_idx(i, m) for i in sa_u]  # we don't exclude m now

    # Special case if the last index is class 0. Then the
    # following class 1 isn't there, but we should treat it
    # as the smallest string in the class.
    SA3 = ([len(x) - 1] if len(x) % 3 == 1 else []) + \
        [i - 1 for i in SA12 if i % 3 == 1]
    SA3 = bucket_sort(x, asize, SA3)
    return merge(x, SA12, SA3)


def skew(x: str) -> list[int]:
    "Skew algorithm for a string."
    y = String(x)
    return skew_rec(y, len(y.alpha))
