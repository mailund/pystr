# Simple exact matching algorithms
from typing import Iterator
from .border_array import border_array


def naive(x: str, p: str,
          progress=False,
          interactive=False,
          ) -> Iterator[int]:
    # If we have an empty string, j is never set,
    # and that can mess up the progress text. So we
    # need to give it a value here, just for that special case.
    j = 0
    for i in range(len(x) - len(p) + 1):
        if progress:
            print(bright_green(f"Iteration {i}"))

        for j in range(len(p)):
            if x[i + j] != p[j]:
                break
        else:
            # We made it through without breaking...
            yield i

        if progress:
            if j == len(p) - 1 and x[i + j] == p[j]:
                naive_show_match(x, p, i)
                print(bright_green(f"We matched at index {i}"))
            else:
                naive_show_mismatch(x, p, i, j)

        if interactive:
            input("Press ENTER to continue")


def border(x: str, p: str,
           progress=False,
           interactive=False
           ) -> Iterator[int]:
    assert p, "Doesn't handle empty patterns"

    # Build the border array
    ba = border_array(p)

    # Now search...
    b = 0
    for i in range(len(x)):
        if progress:
            print(bright_blue(f"Iteration {i}"))
            border_show_prefix_next_comp(x, p, i, b)

        while b > 0 and p[b] != x[i]:
            b = ba[b - 1]
        b = b + 1 if p[b] == x[i] else 0

        if progress:
            border_show_prefix_next_comp(x, p, i + 1, b)
            if b == len(p):
                print(bright_green(f"We matched at index {i - len(p)}"))
                print()

        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]

        if interactive:
            input("Press ENTER to continue")


def kmp(x: str, p: str,
        progress=False,
        interactive=False
        ) -> Iterator[int]:
    
    ba = border_array(p)
    i, j = 0, 0
    while i < len(x):
        
        if progress:
            kmp_show_prefix_next_comp(x, p, i, j)

        while j < len(p) and i < len(x):
            if x[i] != p[j]:
                break
            i += 1
            j += 1

        if j == len(p):
            yield i - len(p)

        if progress:
            kmp_show_prefix_mismatch(x, p, i, j)
            if j == len(p):
                print(bright_green(f"We matched at index {i - len(p)}"))
                print()

        if j == 0:
            i += 1
        else:
            j = ba[j - 1]

        if interactive:
            input("Press ENTER to continue")


# Code for visualising the algorithms...
from .output import clamp                    # noqa: E402
from .cols import yellow, green, red         # noqa: E402
from .cols import bright_green, bright_blue  # noqa: E402


def naive_show_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i]}{green(cx[i:i+j])}{red(cx[i+j])}{cx[i+j+1:]}")
    print(f"{' ' * i}{green(cp[:j])}{red(cp[j])}{cp[j+1:]}")
    print(f"{' ' * (i + j)}j")
    print()


def naive_show_match(x: str, p: str, i: int):
    cx = clamp(x)
    print(f"{' ' * i}i")
    print(f"{cx[:i]}{green(cx[i:i+len(p)])}{cx[i+len(p):]}")
    print(f"{' ' * i}{green(p)}")
    print(f"{' ' * (i + len(p))}j")
    print()


def border_show_prefix_next_comp(x: str, p: str, i: int, b: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-b]}{green(cx[i-b:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - b)}{green(cp[:b])}{yellow(cp[b])}{cp[b+1:]}")
    print(f"{' ' * i}b")
    print()


def border_show_match(x: str, p: str, i: int, b: int):
    cx = clamp(x)
    cp = clamp(p)

    # We don't actually inrease, but this reflects that
    # we have done one comparison...
    i += 1

    print(f"{' ' * i}i")
    print(f"{cx[:i-b]}{green(cx[i-b:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - b)}{green(cp[:b])}{yellow(cp[b])}{cp[b+1:]}")
    print(f"{' ' * i}b")
    print()


def kmp_show_prefix_next_comp(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{yellow(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()


def kmp_show_prefix_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{red(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{red(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()
