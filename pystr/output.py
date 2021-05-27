from dataclasses import dataclass
from typing import Optional


def clamp_index(x: str, i: Optional[int]) -> Optional[int]:
    return min(max(0, i), len(x)) if i is not None else None


@dataclass
class clamp():
    x: str

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.x[idx] if 0 <= idx < len(self.x) else ""
        if isinstance(idx, slice):
            start = clamp_index(self.x, idx.start)
            stop = clamp_index(self.x, idx.stop)
            return self.x[slice(start, stop, idx.step)]
