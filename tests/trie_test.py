"""Test of tries."""

from typing import Callable

from pystr.trie import Trie, TrieNode
from pystr.trie import depth_first_trie
from pystr.trie import breadth_first_trie
from helpers import random_string

# FIXME: make ... a variadic tuple of strings...
TrieConstructor = Callable[..., Trie]


def get_path_label(node: TrieNode) -> str:
    """
    Get the path label for a node.

    This is a slow way to do it, but it is only for testing.
    """
    res: list[str] = []
    while node.parent:
        out, = [k for k, n in node.parent.children.items() if n is node]
        res.append(out)
        node = node.parent
    return ''.join(reversed(res))


def test_simple_trie() -> None:
    """Basic test of trie construction."""
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    # we are testing the comparison impl, so disable
    # linting about it being unecessary
    assert trie == trie  # noqa pylint: disable=comparison-with-itself

    assert "foo" in trie
    assert "foobar" in trie
    assert "bar" in trie
    assert "fo" not in trie
    assert "baz" not in trie


def test_depth_first_trie() -> None:
    """Test that we can build a trie depth-first."""
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == depth_first_trie("foo", "bar", "foobar")


def test_breadth_first_trie() -> None:
    """Test that we can build a trie breadth-first."""
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == breadth_first_trie("foo", "bar", "foobar")


def check_to_dot(constr: TrieConstructor, *x: str) -> None:
    """
    Check that we can write a trie to dot.

    The test isn't that great, since we don't look at the result,
    but that would be pretty hard without actually looking at it.
    We just check that creating the dot-file doesn't crash.
    """
    trie = constr(*x)
    print(trie.to_dot())


def test_simple_to_dot(constr: TrieConstructor = depth_first_trie) -> None:
    """
    Check that we can write a trie to dot.

    The test isn't that great, since we don't look at the result,
    but that would be pretty hard without actually looking at it.
    We just check that creating the dot-file doesn't crash.
    """
    check_to_dot(constr, "foo", "bar", "foobar", "baz", "barfoo")


def test_mississippi_suffixes(
        constr: TrieConstructor = breadth_first_trie) -> None:
    """Test that we can create a trie over all suffixes of mississippi."""
    x = "mississippi"
    strings = [x[i:] for i in range(len(x))]
    trie = constr(*strings)
    print(trie.to_dot())


def check_suffix_links(n: TrieNode) -> None:
    """Check that suffix links are set correctly."""
    if n.parent:
        assert n in n.parent.children.values()

    if n.suffix_link:
        path = get_path_label(n)
        s_path = get_path_label(n.suffix_link)
        assert path.endswith(s_path)
    for v in n.children.values():
        check_suffix_links(v)


def check_suffix_links_suffixes(x: str, constr: TrieConstructor) -> None:
    """Check that suffix links are set correctly."""
    strings = [x[i:] for i in range(len(x))]
    trie = constr(*strings)
    check_suffix_links(trie.root)


def check_trie(constr: TrieConstructor, *x: str) -> None:
    """Do a consistency check on a trie."""
    trie = constr(*x)
    check_suffix_links(trie.root)


def test_abc_b_c_df() -> None:
    """Check trie of abc, b, c."""
    check_trie(depth_first_trie, "abc", "b", "c")


def test_abc_b_c_bf() -> None:
    """Check trie on abc, b, c constructed breadth-first."""
    check_trie(breadth_first_trie, "abc", "b", "c")


def test_suffix_links_abc_df() -> None:
    """Check trie on abc, b, c constructed depth-first."""
    check_suffix_links_suffixes("abc", depth_first_trie)


def test_suffix_links_abc_bf() -> None:
    """Test trie on suffixes of abc."""
    check_suffix_links_suffixes("abc", breadth_first_trie)


def test_suffix_links_mississippi_df() -> None:
    """Check suffix links on mississippi depth-first."""
    check_suffix_links_suffixes("mississippi", depth_first_trie)


def test_suffix_links_mississippi_bf() -> None:
    """Check suffix links on mississippi breadth-first."""
    check_suffix_links_suffixes("mississippi", breadth_first_trie)


def check_suffix_links_random(constr: TrieConstructor) -> None:
    """Check suffix links on random tries."""
    for _ in range(5):
        x = random_string(30)
        strings = [x[i:] for i in range(len(x))]
        trie = constr(*strings)
        check_suffix_links(trie.root)


def test_suffix_links_random_df() -> None:
    """Check suffix links on random tries, depth-first."""
    check_suffix_links_random(depth_first_trie)


def test_suffix_links_random_bf() -> None:
    """Check suffix links on random tries, breadth-first."""
    check_suffix_links_random(breadth_first_trie)


if __name__ == '__main__':
    globs = list(globals().items())
    for name, f in globs:
        if name.startswith("test_"):
            print(name)
            f()
