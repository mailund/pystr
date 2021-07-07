"""Test alphabet code."""

from pystr.alphabet import Alphabet


def test_alphabet() -> None:
    """Test the alphabet class."""
    for x in ["foo", "bar", "baz", "foobar", "bazfoo"]:
        y, alpha = Alphabet.mapped_string_with_sentinel(x)
        assert len(x) == len(y) - 1
        assert len(alpha) == len(set(x)) + 1
        assert len(alpha) == len(set(x)) + 1
        assert alpha.revmap(y[:-1]) == x
        assert ''.join(alpha.revmap(z) for z in y[:-1]) == x

    for x in ["foo", "bar", "baz", "foobar", "bazfoo"]:
        subs, alpha = Alphabet.mapped_subseq(x)
        assert len(subs) == len(x)
        assert alpha.revmap(subs) == x


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
