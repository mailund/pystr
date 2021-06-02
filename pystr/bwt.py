from collections import Counter
from collections.abc import Iterable, Iterator
from .sais import sais  # For the search function

CTAB = dict[str, int]
OTAB = dict[str, list[int]]
SENTINEL = '\x00'


def bw_transform(x: str, sa: list[int]) -> str:
    return ''.join(SENTINEL if i == 0 else x[i - 1] for i in sa)


def c_table(x: str) -> CTAB:
    counts = Counter(x)
    res, acc = {}, 1  # Start at one to skip sentinel
    for char in sorted(counts):
        res[char] = acc
        acc += counts[char]
    return res


def o_table(x: str, sa: list[int], alpha: Iterable[str]) -> OTAB:
    bwt = bw_transform(x, sa)
    res = {char: [0] * (len(bwt) + 1) for char in alpha}
    for z in alpha:
        for i, y in enumerate(bwt):
            res[z][i + 1] = res[z][i] + (y == z)
    return res


def bwt_preprocess(x: str) -> tuple[list[int], CTAB, OTAB]:
    # The BWT search needs to include the sentinel
    # since it will count the character at the end
    # of x incorrectly otherwise (we need it at
    # first line, $x, where we need to count x[-1]).
    sa = sais(x, include_sentinel=True)
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())
    return sa, ctab, otab


def bwt_search_tbls(x: str, p: str,
                    ctab: CTAB, otab: OTAB) -> tuple[int, int]:
    L = 1  # Starting at 0 (the sentinel) handles empty strings
    R = len(x) + 1  # +1 because of the sentinel
    for y in p[::-1]:
        if y not in ctab:
            return 0, 0
        L = ctab[y] + otab[y][L]
        R = ctab[y] + otab[y][R]
        if L >= R:
            return 0, 0

    # if we search for the empty string, we will include
    # the sentinel position in the output. We never should
    L += (L == 0)
    return L, R


def bwt_search(x: str, p: str) -> Iterator[int]:
    sa, ctab, otab = bwt_preprocess(x)
    L, R = bwt_search_tbls(x, p, ctab, otab)
    for i in range(L, R):
        yield sa[i]
