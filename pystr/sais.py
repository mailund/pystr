import BitVector as bv
from subseq import isseq, imseq


def map_string(x: str) -> tuple[isseq, int]:
    letters = {*x}
    alphabet = {
        a: i + 1
        for i, a in enumerate(sorted(letters))
    }
    new_string = list(alphabet[a] for a in x)
    new_string.append(0)  # add sentinel
    return isseq(new_string), len(alphabet) + 1


def classify_SL(is_S: bv.BitVector, x: isseq) -> None:
    last = len(x) - 1
    is_S[last] = True
    for i in reversed(range(last - 1)):
        is_S[i] = x[i] < x[i+1] or (x[i] == x[i+1] and is_S[i+1])


def is_LMS(is_S: bv.BitVector, i: int) -> bool:
    return 0 if i == 0 else is_S[i] and not is_S[i - 1]


def sais_rec(x: isseq, sa: imseq, asize: int,
             is_S: bv.BitVector):

    if len(x) == asize:
        # base case...
        for i, a in enumerate(x):
            sa[a] = i
        return


def sais(x: str) -> list[int]:
    s, asize = map_string(x)
    sa = [0] * len(s)
    is_S = bv.BitVector(size=len(s))
    sais_rec(s, imseq(sa), asize, is_S)
    return sa[1:]


if __name__ == '__main__':
    x = "mississippi"
    print(map_string(x))
    is_S = bv.BitVector(size=len(x))
    classify_SL(is_S, x)
    print(is_S)
