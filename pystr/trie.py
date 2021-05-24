from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional, TypeVar, NamedTuple
from .subseq import subseq


T = TypeVar("T")
S = TypeVar("S")


@dataclass(eq=False)
class TrieNode:
    label: Optional[int] = None
    out: dict[str, TrieNode] = field(default_factory=dict)

    def __eq__(self, other) -> bool:
        return type(other) == type(self) and \
            sorted(self.out) == sorted(other.out) and \
            all(self.out[k] == other.out[k] for k in self.out)


@dataclass(eq=False)
class Trie:
    root: TrieNode = field(default_factory=TrieNode)

    def insert(self, x: str, label: int):
        n = self.root
        for i in range(len(x)):
            if x[i] not in n.out:
                n.out[x[i]] = TrieNode()
            n = n.out[x[i]]
        n.label = label

    def __contains__(self, x: str) -> bool:
        n = self.root
        for i in range(len(x)):
            if x[i] not in n.out:
                return False
            n = n.out[x[i]]
        return n.label is not None

    def __eq__(self, other) -> bool:
        return type(other) == type(self) and self.root == other.root


def depth_first_trie(*strings: str) -> Trie:
    """The simplest construction just insert one string at a time."""
    trie = Trie()
    for i, x in enumerate(strings):
        trie.insert(x, i)
    return trie


# Labelled strings...
LS = NamedTuple('LS', [('label', int), ('x', subseq[str])])


def breadth_first_trie_rec(strings: list[LS]) -> TrieNode:
    empty = [label for label, x in strings if len(x) == 0]
    assert len(empty) <= 1
    node = TrieNode(label=(empty[0] if len(empty) == 1 else None))

    non_empty = [LS(label, x) for label, x in strings if len(x) != 0]
    out_groups = defaultdict(list)
    for label, x in non_empty:
        out_groups[x[0]].append(LS(label, x[1:]))
    for k in out_groups:
        node.out[k] = breadth_first_trie_rec(out_groups[k])
    return node


def breadth_first_trie(*strings: str) -> Trie:
    labelled = list(LS(i, subseq[str](x)) for i, x in enumerate(strings))
    return Trie(breadth_first_trie_rec(labelled))
