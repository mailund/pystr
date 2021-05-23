from pystr.trie import Trie


def test_simple_trie():
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert "foo" in trie
    assert "foobar" in trie
    assert "bar" in trie
    assert "fo" not in trie
    assert "baz" not in trie
