"""Functions for constructing border arrays."""


def border_array(x: str) -> list[int]:
    """Construct the border array for x."""
    ba = [0] * len(x)
    for j in range(1, len(x)):
        b = ba[j - 1]
        while b > 0 and x[j] != x[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if x[j] == x[b] else 0
    return ba


def strict_border_array(x: str) -> list[int]:
    """
    Construct the strict border array for x.

    A struct border array is one where the border cannot
    match on the next character. If b is the length of the
    longest border for x[:i+1], it means x[:b] == x[i-b:i+1],
    but for a strict border, it must be the longest border
    such that x[b] != x[i+1].
    """
    ba = border_array(x)
    for j, b in enumerate(ba[:-1]):
        if x[b] == x[j + 1] and b > 0:
            ba[j] = ba[b - 1]
    return ba
