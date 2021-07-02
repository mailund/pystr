import typing
from .trie import TrieNode, depth_first_trie


def occurrences(n: TrieNode) -> typing.Iterator[int]:
    """Iterate over all occurrances in the out-list of a node."""
    if n.label is not None:
        yield n.label

    olist = n.out_list
    while olist:
        assert olist.label is not None
        yield olist.label
        olist = olist.out_list


def find_out(n: TrieNode, a: str) -> TrieNode:
    """Find the node we get to with an a move.

    We will end up in the node if we cannot make one,
    but that works fine with the out list reporting."""
    while not n.is_root and a not in n:
        assert n.suffix_link is not None
        n = n.suffix_link
    return n[a] if a in n else n


def aho_corasick(x: str, *p: str
                 ) -> typing.Iterator[tuple[int, int]]:
    """Exact pattern matching with the Aho-Corasick algorithm."""
    trie = depth_first_trie(*p)
    n = trie.root

    # If the empty string is in the trie we
    # need to handle it as a special case
    if n.label is not None:
        yield (n.label, 0)

    for i, a in enumerate(x):
        n = find_out(n, a)
        for label in occurrences(n):
            yield (label, i - len(p[label]) + 1)
