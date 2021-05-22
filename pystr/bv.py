
class BitVector:
    bytes: bytearray
    size: int

    def __init__(self, size: int):
        self.size = size
        # FIXME: not sure if this is the right calculation, it can
        # overshoot a bit... fix it later
        self.bytes = bytearray((size+1) // 8 + 1)

    def __getitem__(self, i: int) -> bool:
        return bool(self.bytes[i//8] & (1 << (i % 8)))

    def __setitem__(self, i: int, v: bool):
        if v:
            self.bytes[i//8] = self.bytes[i//8] | (1 << (i % 8))
        else:
            self.bytes[i//8] = self.bytes[i//8] & ~(1 << (i % 8))

    def __len__(self) -> int:
        return self.size
