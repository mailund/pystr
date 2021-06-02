
def border_array(x: str) -> list[int]:
    ba = [0] * len(x)
    for j in range(1, len(x)):
        b = ba[j - 1]
        while b > 0 and x[j] != x[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if x[j] == x[b] else 0
    return ba


def strict_border_array(x: str) -> list[int]:
    print("sb on", x)
    # If we start with strict as a copy we don't need to handle the last index
    # as a special case for empty strings
    ba = border_array(x)
    strict = ba[:]

    # loop over ba instead of index handles empty  lists.
    for j, b in enumerate(ba[:-1]):
        print(b, x[b], x[j+1], '=>', b if x[b] != x[j+1] else strict[b])
        strict[j] = b if x[b] != x[j+1] else strict[b]
    print()
    print(strict)

    if not x:
        return []
    strict = [0] * len(x)
    for j in range(len(x) - 1):
        print(ba[j], x[ba[j]], x[j+1], '=>', ba[j]
              if x[ba[j]] != x[j+1] else strict[ba[j]])
        strict[j] = ba[j] if x[ba[j]] != x[j+1] else strict[ba[j]]
    strict[-1] = ba[-1]
    print()
    print(strict)
    print()

    return strict
