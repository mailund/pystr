"""Test subseq class."""

from pystr import subseq


def test_substr() -> None:
    """Test that we can work with substrings."""
    underlying = "mississippi"
    assert subseq.SubSeq[str](underlying) == underlying
    assert subseq.SubSeq[str](underlying, 1) == underlying[1:]
    assert subseq.SubSeq[str](underlying, 1, 5) == underlying[1:5]

    x: subseq.SubSeq[str] = subseq.SubSeq[str](underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y: str = underlying[1:6]
    assert x == y
    assert str(x) == str(y)
    for i, _ in enumerate(x):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z: subseq.SubSeq[str] = subseq.SubSeq[str](underlying)
    assert z[:] == underlying
    assert z[:] == z


def test_int_subseq() -> None:
    """Test that we can make subseqs of int lists."""
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    assert subseq.SubSeq[int](underlying) == underlying
    assert subseq.SubSeq[int](underlying, 1) == underlying[1:]
    assert subseq.SubSeq[int](underlying, 1, 5) == underlying[1:5]

    x: subseq.SubSeq[int] = subseq.SubSeq[int](underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y: list[int] = underlying[1:6]
    assert x == y
    for i, _ in enumerate(x):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z: subseq.SubSeq[int] = subseq.SubSeq[int](underlying)
    assert z[:] == underlying
    assert z[:] == z

    w: subseq.SubSeq[int] = z[-4:-2]
    assert w[:] == underlying[-4:-2]


def test_mutable() -> None:
    """Test mutable subseqs."""
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    x: subseq.MSubSeq[int] = subseq.MSubSeq[int](underlying, 1)
    x[1] = 42
    assert x[1] == 42
    y = x[2:]
    # assignment works. I don't know what pylint has been drinking,
    # but it doesn't understand the type system, that's for sure.
    y[2] = 13  # pylint: disable=unsupported-assignment-operation
    assert y[2] == x[4] == underlying[5]
    x[1:5] = 17
    assert x[1:5] == [17, 17, 17, 17]


def test_compare() -> None:
    """Test that we can compare subseqs."""
    x = subseq.SubSeq[int]([1, 2, 3])
    y = subseq.SubSeq[int]([1, 2, 3, 4])
    z = subseq.SubSeq[int]([1, 3])
    assert x < y and y > x and not y < x  # pylint: disable=unneeded-not
    assert x < z and z > x and not z < x  # pylint: disable=unneeded-not
    assert y < z and z > y and not z < y  # pylint: disable=unneeded-not


def test_assigments() -> None:
    """Test that we can assign to subseqs."""
    x = [1, 2, 3, 4]
    sub: subseq.MSubSeq[int] = subseq.MSubSeq[int](x)
    assert x == sub
    sub[:] = -1
    assert sub == [-1, -1, -1, -1]
    assert x == [-1, -1, -1, -1]


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
