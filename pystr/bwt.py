import collections
import typing
from .sais import sais  # For the search function

CTAB = dict[str, int]
OTAB = dict[str, list[int]]
SENTINEL = '\x00'


def bw_transform(x: str, sa: list[int]) -> str:
    return ''.join(SENTINEL if i == 0 else x[i - 1] for i in sa)


def c_table(x: str) -> CTAB:
    counts = collections.Counter(x)
    res, acc = {}, 1  # Start at one to skip sentinel
    for char in sorted(counts):
        res[char] = acc
        acc += counts[char]
    return res


def o_table(x: str,
            sa: list[int],
            alpha: typing.Iterable[str]
            ) -> OTAB:
    bwt = bw_transform(x, sa)
    res = {char: [0] * (len(bwt) + 1) for char in alpha}
    for z in alpha:
        for i, y in enumerate(bwt):
            res[z][i + 1] = res[z][i] + (y == z)
    return res


def bwt_preprocess(x: str) -> tuple[list[int], CTAB, OTAB]:
    sa = sais(x)
    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())
    return sa, ctab, otab


def bwt_search_tbls(x: str, p: str,
                    ctab: CTAB, otab: OTAB) -> tuple[int, int]:
    L = 0  # Starting at 0 (the sentinel) handles empty strings
    R = len(x) + 1  # +1 because of the sentinel
    for y in p[::-1]:
        if y not in ctab:
            return 0, 0
        L = ctab[y] + otab[y][L]
        R = ctab[y] + otab[y][R]
        if L >= R:
            return 0, 0
    return L, R


def bwt_search(x: str, p: str) -> typing.Iterator[int]:
    sa, ctab, otab = bwt_preprocess(x)
    L, R = bwt_search_tbls(x, p, ctab, otab)
    assert L <= R, "R should never be smaller than L."
    for i in range(L, R):
        yield sa[i]
