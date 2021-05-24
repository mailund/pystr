from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Optional, TypeVar, NamedTuple
from typing import cast
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
    out_list: Optional[TrieNode] = field(default=None, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def to_dot(self, res: list[str]) -> list[str]:
        if self.label is None:
            res.append(f'{id(self)}[label="", shape=point]')
        else:
            res.append(f'{id(self)}[label="{self.label}", shape=circle]')

        if self.suffix_link is not None and not self.suffix_link.is_root:
            res.append(f"{id(self)} -> {id(self.suffix_link)}[style=dotted, color=red]") # noqal
        if self.out_list is not None and not self.out_list.is_root:
            res.append(f"{id(self)} -> {id(self.out_list)}[style=dotted, color=green]") # noqal

        for k, n in self.out.items():
            res.append(f'{id(self)} -> {id(n)}[label="{k}"]')
            n.to_dot(res)
        res.append("{ rank = same;" +
                   ";".join(str(id(n)) for n in self.out.values()) +
                   "}")

        return res

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

    def to_dot(self) -> str:
        return 'digraph { rankdir="LR" ' + \
            '\n'.join(self.root.to_dot([])) + \
            '}'

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
    root.out_list = root.suffix_link = root

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
            # In the groups, slice off the first character for
            # the next level... (subseq makes this O(1)).
            out_groups[x[0]].append(LS(label, x[1:]))

        # Take the groups, make a node for each (and insert the
        # nodes as children of `node`), and put the new node and
        # strings in the queue for further processing. Update suffix
        # link and out list before we insert the new node in the parent
        # or we would have to handle special cases in the root
        for k, labelled in out_groups.items():
            child = TrieNode(parent=node)

            # We get the suffix link by running up the links from the
            # parent and trying to extend them.
            p_suffix = cast(TrieNode, node.suffix_link)
            while not p_suffix.is_root and k not in p_suffix.out:
                p_suffix = cast(TrieNode, p_suffix.suffix_link)
            # Now we can either extend or we are in the root.
            child.suffix_link = \
                p_suffix.out[k] \
                if k in p_suffix.out \
                else p_suffix

            child.out_list = \
                child.suffix_link \
                if child.suffix_link.label is not None \
                else child.suffix_link.out_list

            node.out[k] = child
            queue.append((child, labelled))

    return Trie(root)
