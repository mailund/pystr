from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Optional, TypeVar, NamedTuple
from .subseq import subseq


T = TypeVar("T")
S = TypeVar("S")
LS = NamedTuple('LS', [('label', int), ('x', subseq[str])])


@dataclass(eq=False)
class TrieNode:
    label: Optional[int] = None
    out: dict[str, TrieNode] = field(default_factory=dict)
    parent: Optional[TrieNode] = field(default=None, repr=False)
    suffix_link: Optional[TrieNode] = field(default=None, repr=False)

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
                n.out[x[i]] = TrieNode(parent=n)
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


def breadth_first_trie(*strings: str) -> Trie:
    labelled = list(LS(i, subseq[str](x)) for i, x in enumerate(strings))
    root = TrieNode()
    queue = deque[tuple[TrieNode, list[LS]]]()
    if labelled:  # Only do something if the input wasn't empty...
        queue.append((root, labelled))

    while queue:
        node, labelled = queue.popleft()

        # If there is an empty string (and only one is allowed)
        # then it ends in `node` and gives us its label.
        empty = [label for label, x in labelled if len(x) == 0]
        assert len(empty) <= 1
        if len(empty) == 1:
            node.label = empty[0]

        # If there are non-empty strings we gropy them by the
        # first character. Each group will be a sub-mode.
        non_empty = [ls for ls in labelled if len(ls.x) != 0]
        out_groups: dict[str, list[LS]] = defaultdict(list)
        for label, x in non_empty:
            out_groups[x[0]].append(LS(label, x[1:]))

        # Take the groups, make a node for each (and insert the
        # nodes as children of `node`), and put the new node and
        # strings in the queue for further processing.
        for k, labelled in out_groups.items():
            node.out[k] = TrieNode(parent=node)
            queue.append((node.out[k], labelled))

    return Trie(root)
