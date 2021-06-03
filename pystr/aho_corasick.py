from .trie import TrieNode, depth_first_trie
from typing import Iterator, cast


def occurrences(n: TrieNode) -> Iterator[int]:
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


def aho_corasick(x: str, *p: str) -> Iterator[tuple[int, int]]:
    trie = depth_first_trie(*p)
    n = trie.root

    # If the empty string is in the trie we
    # need to handle it as a special case
    if n.label is not None:
        yield (n.label, 0)

    for i in range(len(x)):
        n = find_out(n, x[i])
        for label in occurrences(n):
            yield (label, i - len(p[label]) + 1)
