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

    # These are only needed for the Aho-Corasick algorithm, not for
    # basic use of a trie.
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
    # This is all it takes to build the trie.
    trie = Trie()
    for i, x in enumerate(strings):
        trie.insert(x, i)

    # If we want the suffix link and out list as well,
    # we need a breadth first traversal for that.
    queue = deque[TrieNode]([trie.root])
    while queue:
        n = queue.popleft()
        for out_edge, child in n.out.items():
            set_suffix_link(child, out_edge)
            queue.append(child)

    return trie


def set_suffix_link(node: TrieNode, in_edge: str):
    # We get the suffix link by running up the links from the
    # parent and trying to extend them. Casts are for the type
    # checker, telling them that nodes are not None
    parent = cast(TrieNode, node.parent)
    if parent.is_root:
        node.suffix_link = parent
    else:
        suffix = cast(TrieNode, parent.suffix_link)
        while in_edge not in suffix.out and not suffix.is_root:
            suffix = cast(TrieNode, suffix.suffix_link)

        # Now we can either extend or we are in the root.
        if in_edge in suffix.out:
            node.suffix_link = suffix.out[in_edge]
        else:
            # If we can't extend, we want the root (== suffix)
            node.suffix_link = suffix

    # The out list either skips suffix_link or not, depending on
    # whether there is a label there or not.
    if node.suffix_link.label is not None:
        node.out_list = node.suffix_link
    else:
        node.suffix_link.out_list


def breadth_first_trie(*strings: str) -> Trie:
    labelled = list(LS(i, subseq[str](x)) for i, x in enumerate(strings))

    root_lab, root_groups = group_strings(labelled)
    root = TrieNode(label=root_lab)

    queue = deque[tuple[TrieNode, dict[str, list[LS]]]]()
    queue.append((root, root_groups))

    while queue:
        parent, groups = queue.popleft()
        for edge, group in groups.items():
            node_lab, node_groups = group_strings(group)
            parent.out[edge] = TrieNode(label=node_lab, parent=parent)
            queue.append((parent.out[edge], node_groups))
            set_suffix_link(parent.out[edge], edge)

    return Trie(root)


def group_strings(strings: list[LS]) -> \
        tuple[Optional[int], dict[str, list[LS]]]:

    """Split input into groups according to first character.
If there is an empty string in the input, get its label.
Returns the label (or None) and the groups in a dict."""

    empty, non_empty = list[LS](), list[LS]()
    for ls in strings:
        (non_empty, empty)[len(ls.x) == 0].append(ls)

    assert(len(empty) <= 1)
    label = empty[0].label if len(empty) == 1 else None

    out_groups = defaultdict[str, list[LS]](list)
    for lab, x in non_empty:
        # In the groups, slice off the first character for
        # the next level... (subseq makes this O(1)).
        out_groups[x[0]].append(LS(lab, x[1:]))

    return label, out_groups
