from pystr.alphabet_string import String


def test_alphabet() -> None:
    for x in ["foo", "bar", "baz", "foobar", "bazfoo"]:
        y = String(x)
        assert len(x) == len(y) - 1
        assert len(y.alpha) == len(set(x)) + 1
        assert len(y.alpha) == len(set(x)) + 1
        assert str(y[:-1]) == x


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
