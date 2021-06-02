
def border_array(x: str) -> list[int]:
    ba = [0] * len(x)
    for j in range(1, len(x)):
        b = ba[j - 1]
        while b > 0 and x[j] != x[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if x[j] == x[b] else 0
    return ba


def strict_border_array(x: str) -> list[int]:
    ba = border_array(x)
    strict = [0] * len(x)
    for j, b in enumerate(ba):
        if b == 0 or j == len(x) - 1 or x[b] != x[j+1]:
            strict[j] = b
        else:
            strict[j] = strict[b - 1]
    return strict
