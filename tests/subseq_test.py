__import__("testsetup")
from pystr.subseq import subseq, mutsubseq, substr


def test_substr():
    underlying = "mississippi"
    assert substr(underlying) == underlying
    assert substr(underlying, 1) == underlying[1:]
    assert substr(underlying, 1, 5) == underlying[1:5]

    x = substr(underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y = underlying[1:6]
    assert x == y
    assert str(x) == str(y)
    for i in range(len(x)):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z = substr(underlying)
    assert z[:] == underlying
    assert z[:] == z


def test_int_subseq():
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    assert subseq(underlying) == underlying
    assert subseq(underlying, 1) == underlying[1:]
    assert subseq(underlying, 1, 5) == underlying[1:5]

    x = subseq(underlying, 1, 6)
    assert x == underlying[1:6]
    for i, a in enumerate(x):
        assert underlying[1 + i] == a

    y = underlying[1:6]
    assert x == y
    for i in range(len(x)):
        assert x[i] == y[i]
        assert x[i:] == y[i:]

    z = subseq(underlying)
    assert z[:] == underlying
    assert z[:] == z


def test_mutable():
    underlying = [2, 1, 4, 4, 1, 4, 4, 1, 3, 3, 1, 0]
    x = mutsubseq(underlying, 1)
    x[1] = 42
    assert x[1] == 42
    y = x[2:]
    y[2] = 13
    assert y[2] == x[4] == underlying[5]
    x[1:5] = 17
    assert x[1:5] == [17, 17, 17, 17]


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
