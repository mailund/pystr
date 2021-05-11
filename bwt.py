from collections import Counter
from collections.abc import Iterable

CTAB = dict[str, int]
OTAB = dict[str, list[int]]

# I don't use the terminal sentinel in any of this code (except
# indirectly when constructing the suffix array. It isn't necessary
# once I have the suffix array and the prefix-problem is taken
# care of).


def bwt(x: str, sa: list[int]) -> str:
    # This works because index -1 is index n-1.
    return ''.join(x[i - 1] for i in sa)


def c_table(x: str) -> CTAB:
    counts = Counter(x)
    res, acc = {}, 0
    for char in sorted(counts):
        res[char] = acc
        acc += counts[char]
    return res


def o_table(x: str, sa: list[int], alpha: Iterable[str]) -> OTAB:
    res = {char: [0] * (len(x) + 1) for char in alpha}
    for z in alpha:
        for i, y in enumerate(bwt(x, sa)):
            res[z][i + 1] = res[z][i] + (y == z)
    return res


def bwt_search(x: str, p: str, ctab: CTAB, otab: OTAB) -> tuple[int, int]:
    L, R = 0, len(x)
    for y in p[::-1]:
        if y not in ctab:
            return 0, 0
        L = ctab[y] + otab[y][L]
        R = ctab[y] + otab[y][R]
        if L >= R:
            return 0, 0
    return L, R


if __name__ == '__main__':
    from skew import skew
    x = 'mississippi'
    sa = skew(x)
    for i, j in enumerate(sa):
        print("{:2d}".format(i), x[j:] + x[:j])
    print()

    ctab = c_table(x)
    otab = o_table(x, sa, ctab.keys())
    L, R = bwt_search(x, "is", ctab, otab)
    for i in range(L, R):
        print(sa[i], x[sa[i]:])
