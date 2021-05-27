from dataclasses import dataclass
from typing import Optional


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
