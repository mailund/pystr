from pystr.trie import Trie
from pystr.trie import depth_first_trie
from pystr.trie import breadth_first_trie


def test_simple_trie():
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == trie

    assert "foo" in trie
    assert "foobar" in trie
    assert "bar" in trie
    assert "fo" not in trie
    assert "baz" not in trie


def test_depth_first_trie():
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == depth_first_trie("foo", "bar", "foobar")


def test_breadth_first_trie():
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == breadth_first_trie("foo", "bar", "foobar")


def test_simple_to_dot():
    trie = breadth_first_trie("foo", "bar", "foobar", "baz", "barfoo")
    print(trie.to_dot())


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
