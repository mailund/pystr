
class BitVector:
    """A bit vector."""

    bytes: bytearray
    size: int

    def __init__(self, size: int):
        """Creates a BitVector that can hold size bits"""
        self.size = size
        self.bytes = bytearray((size+8-1)//8)

    def __getitem__(self, i: int) -> bool:
        """Gets bit number i in the vector."""
        return bool(self.bytes[i//8] & (1 << (i % 8)))

    def __setitem__(self, i: int, v: bool) -> None:
        """Sets bit number i in the vector."""
        if v:
            self.bytes[i//8] = self.bytes[i//8] | (1 << (i % 8))
        else:
            self.bytes[i//8] = self.bytes[i//8] & ~(1 << (i % 8))

    def __len__(self) -> int:
        """Returns the length of the vector."""
        return self.size
