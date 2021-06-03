

def indent(i: int) -> str:
    return ' ' * i


def place_pointers(*pointers: tuple[str, int]) -> str:
    m = max(p[1] for p in pointers)
    out = [' '] * (m + 1)
    for name, loc in pointers:
        out[loc] = name
    return ''.join(out)
