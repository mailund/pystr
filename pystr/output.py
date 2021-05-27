from dataclasses import dataclass
from typing import Optional
from .cols import yellow, green, red


@dataclass
class clamp():
    x: str

    def __getitem__(self, idx):
        if isinstance(idx, int):
            if 0 <= idx < len(self.x):
                return self.x[idx]
            else:
                return ""
        if isinstance(idx, slice):
            start = self.clamp(idx.start)
            stop = self.clamp(idx.stop)
            return self.x[slice(start, stop, idx.step)]

    def clamp(self, i: Optional[int]) -> Optional[int]:
        if i is None:
            return i
        if i < 0:
            return 0
        if i >= len(self.x):
            return len(self.x)
        return i


def show_prefix_next_comp(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{yellow(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{yellow(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()


def show_prefix_mismatch(x: str, p: str, i: int, j: int):
    cx = clamp(x)
    cp = clamp(p)
    print(f"{' ' * i}i")
    print(f"{cx[:i-j]}{green(cx[i-j:i])}{red(cx[i])}{cx[i+1:]}")
    print(f"{' ' * (i - j)}{green(cp[:j])}{red(cp[j])}{cp[j+1:]}")
    print(f"{' ' * i}j")
    print()
