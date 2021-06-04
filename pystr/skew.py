"""
Straightforward implementation of the skew/DC3 algorithm

    - https://www.cs.helsinki.fi/u/tpkarkka/publications/jacm05-revised.pdf

"""

from typing import Sequence

SkewTriplet = tuple[int, int, int]
SkewTripletDict = dict[SkewTriplet, int]

# We only explicitly use this for the central sentinel,
# but it is the same for the terminal sentinel
SENTINEL = 0
SENTINEL_TRIP = (SENTINEL, SENTINEL, SENTINEL)


def safe_idx(x: Sequence[int], i: int) -> int:
    "Hack to get zero if we index beyond the end."
    return SENTINEL if i >= len(x) else x[i]


def symbcount(x: list[int], asize: int) -> list[int]:
    "Count how often we see each character in the alphabet."
    # This is what collections.Counter does, but we need the
    # alphabet to be sorted integers, so we do it manually.
    counts = [0] * asize
    for c in x:
        counts[c] += 1
    return counts


def cumsum(counts: list[int]) -> list[int]:
    "Compute the cumulative sum from the character count."
    res, acc = [0] * len(counts), 0
    for i, k in enumerate(counts):
        res[i] = acc
        acc += k
    return res


def bucket_sort(x: list[int], asize: int,
                idx: list[int], offset: int = 0) -> list[int]:
    "Sort indices in idx according to x[i + offset]."
    sort_symbs = [safe_idx(x, i + offset) for i in idx]
    counts = symbcount(sort_symbs, asize)
    buckets = cumsum(counts)
    out = [0] * len(idx)
    for i in idx:
        bucket = safe_idx(x, i + offset)
        out[buckets[bucket]] = i
        buckets[bucket] += 1
    return out


def radix3(x: list[int], asize: int, idx: list[int]) -> list[int]:
    "Sort indices in idx according to their first three letters in x."
    idx = bucket_sort(x, asize, idx, 2)
    idx = bucket_sort(x, asize, idx, 1)
    return bucket_sort(x, asize, idx)


def triplet(x: Sequence[int], i: int) -> SkewTriplet:
    "Extract the triplet (x[i],x[i+1],x[i+2])."
    assert i < len(x), "Don't create empty triplets!"
    return (safe_idx(x, i), safe_idx(x, i + 1), safe_idx(x, i + 2))


def collect_alphabet(x: list[int], idx: list[int]) -> SkewTripletDict:
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


def less(x: list[int], i: int, j: int, ISA: dict[int, int]) -> bool:
    "Check if x[i:] < x[j:] using the inverse suffix array for SA12."
    a, b = safe_idx(x, i), safe_idx(x, j)
    if a < b:
        return True
    if a > b:
        return False
    if i % 3 != 0 and j % 3 != 0:
        return ISA[i] < ISA[j]
    return less(x, i + 1, j + 1, ISA)


def merge(x: list[int], SA12: list[int], SA3: list[int]) -> list[int]:
    "Merge the suffixes in sorted SA12 and SA3."
    # I'm using a dict here, but you can use a list with a little
    # arithmetic
    ISA = {SA12[i]: i for i in range(len(SA12))}
    SA = []
    i, j = 0, 0
    while i < len(SA12) and j < len(SA3):
        if less(x, SA12[i], SA3[j], ISA):
            SA.append(SA12[i])
            i += 1
        else:
            SA.append(SA3[j])
            j += 1
    SA.extend(SA12[i:])
    SA.extend(SA3[j:])
    return SA


def build_u(x: list[int], alpha: SkewTripletDict) -> list[int]:
    "Construct u string, using 1 as central sentinel."
    # By putting the i % 3 == 1 indices first, we know that the central
    # sentinel will always be at len(u) // 2.
    return [*(alpha[triplet(x, i)] for i in range(1, len(x), 3)),
            SENTINEL,
            *(alpha[triplet(x, i)] for i in range(2, len(x), 3))]


def u_idx(i: int, m: int) -> int:
    "Map indices in u back to indices in the original string."
    return 1 + 3 * i if i < m else 2 + 3 * (i - m - 1)


def skew_rec(x: list[int], asize: int) -> list[int]:
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


def skew(x: str, include_sentinel: bool = True) -> list[int]:
    "Skew algorithm for a string."
    # The skew_rec() function wants a list of integers,
    # so we convert the string in the first call.
    # It is only because of the safe_idx() hack that we
    # need to convert the string; without it, we could work
    # with both str and list[int], but the sentinel we generate
    # is int, and we have to compare letters, so all letters must
    # then be int.
    # I am assuming that the alphabet size is 256 here, although
    # of course it might not be. It is a simplification instead of
    # remapping the string.
    istring = [ord(y) for y in x]
    # Build the sa without sentinel (we have it implicitly), and
    # then add it afterwards if we want it
    sa = skew_rec(istring, 256)
    return [len(x)] + sa if include_sentinel else sa
