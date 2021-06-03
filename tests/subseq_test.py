from pystr.subseq import subseq, msubseq, substr, isseq, misseq


def test_substr() -> None:
    underlying = "mississippi"
    assert substr(underlying) == underlying
    assert substr(underlying, 1) == underlying[1:]
    assert substr(underlying, 1, 5) == underlying[1:5]

    x: substr = substr(underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y: str = underlying[1:6]
    assert x == y
    assert str(x) == str(y)
    for i in range(len(x)):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z: substr = substr(underlying)
    assert z[:] == underlying
    assert z[:] == z


def test_int_subseq() -> None:
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    assert subseq(underlying) == underlying
    assert subseq(underlying, 1) == underlying[1:]
    assert subseq(underlying, 1, 5) == underlying[1:5]

    x: subseq[int] = subseq(underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y: list[int] = underlying[1:6]
    assert x == y
    for i in range(len(x)):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z: subseq[int] = subseq(underlying)
    assert z[:] == underlying
    assert z[:] == z


def test_mutable() -> None:
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    x: msubseq[int] = msubseq(underlying, 1)
    x[1] = 42
    assert x[1] == 42
    y = x[2:]
    y[2] = 13
    assert y[2] == x[4] == underlying[5]
    x[1:5] = 17
    assert x[1:5] == [17, 17, 17, 17]


def test_compare() -> None:
    x, y, z = isseq([1, 2, 3]), isseq([1, 2, 3, 4]), isseq([1, 3])
    assert x < y and y > x and not y < x
    assert x < z and z > x and not z < x
    assert y < z and z > y and not z < y


def test_assigments() -> None:
    x = [1, 2, 3, 4]
    ss: misseq = misseq(x)
    assert x == ss
    ss[:] = -1
    assert ss == [-1, -1, -1, -1]
    assert x == [-1, -1, -1, -1]


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
