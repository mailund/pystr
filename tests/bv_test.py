"""Test of bitvectors."""

from pystr.bv import BitVector


def test_v() -> None:
    """Basic test of bitvector."""
    bvec = BitVector(4)
    for i in range(4):
        assert not bvec[i]

    bvec[1] = True
    bvec[3] = True
    for i in [0, 2]:
        assert not bvec[i]
    for i in [1, 3]:
        assert bvec[i]

    expected = [False, True, False, True]
    for i, b in enumerate(bvec):
        assert b == expected[i]

    bvec[1] = False
    bvec[3] = False
    for i in range(4):
        assert not bvec[i]
