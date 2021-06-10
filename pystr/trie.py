from __future__ import annotations
import dataclasses
import collections
import typing

from .subseq import SubSeq


T = typing.TypeVar("T")
S = typing.TypeVar("S")
LS = typing.NamedTuple('LS', [('label', int), ('x', SubSeq[str])])


@dataclasses.dataclass(eq=False)
class TrieNode:
    label: typing.Optional[int] = None
    children: dict[str, TrieNode] = \
        dataclasses.field(default_factory=dict)

    # These are only needed for the Aho-Corasick algorithm, not for
    # basic use of a trie.
    parent: typing.Optional[TrieNode] = \
        dataclasses.field(default=None, repr=False)
    suffix_link: typing.Optional[TrieNode] = \
        dataclasses.field(default=None, repr=False)
    out_list: typing.Optional[TrieNode] = \
        dataclasses.field(default=None, repr=False)

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def __getitem__(self, a: str) -> TrieNode:
        # This just makes the code a little nicer
        # to look at, avoiding the .children[].
        return self.children[a]

    def __setitem__(self, a: str, n: TrieNode) -> None:
        self.children[a] = n

    def __contains__(self, a: str) -> bool:
        return a in self.children

    def to_dot(self, res: list[str]) -> list[str]:
        if self.label is None:
            res.append(f'{id(self)}[label="", shape=point]')
        else:
            res.append(f'{id(self)}[label="{self.label}", shape=circle]')

        if self.suffix_link is not None and not self.suffix_link.is_root:
            res.append(f"{id(self)} -> {id(self.suffix_link)}[style=dotted, color=red]")  # noqa: E501
        if self.out_list is not None:
            res.append(f"{id(self)} -> {id(self.out_list)}[style=dotted, color=green]")   # noqa: E501

        for k, n in self.children.items():
            res.append(f'{id(self)} -> {id(n)}[label="{k}"]')
            n.to_dot(res)
        res.append("{ rank = same;" +
                   ";".join(str(id(n)) for n in self.children.values()) +
                   "}")

        return res

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrieNode):  # pragma: no cover
            raise NotImplementedError()
        return \
            sorted(self.children) == sorted(other.children) and \
            all(self[k] == other[k] for k in self.children)


@dataclasses.dataclass(eq=False)
class Trie:
    root: TrieNode = \
        dataclasses.field(default_factory=TrieNode)

    def insert(self, x: str, label: int) -> None:
        n = self.root
        for i in range(len(x)):
            if x[i] not in n:
                n[x[i]] = TrieNode(parent=n)
            n = n[x[i]]
        n.label = label

    def __contains__(self, x: str) -> bool:
        n = self.root
        for i in range(len(x)):
            if x[i] not in n:
                return False
            n = n[x[i]]
        return n.label is not None

    def to_dot(self) -> str:
        return 'digraph { rankdir="LR" ' + \
            '\n'.join(self.root.to_dot([])) + \
            '}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trie):  # pragma: no cover
            raise NotImplementedError()
        return type(other) == type(self) and self.root == other.root


def depth_first_trie(*strings: str) -> Trie:
    """The simplest construction just insert one string at a time."""
    # This is all it takes to build the trie.
    trie = Trie()
    for i, x in enumerate(strings):
        trie.insert(x, i)

    # If we want the suffix link and out list as well,
    # we need a breadth first traversal for that.
    queue = collections.deque[TrieNode]([trie.root])
    while queue:
        n = queue.popleft()
        for out_edge, child in n.children.items():
            set_suffix_link(child, out_edge)
            queue.append(child)

    return trie


def set_suffix_link(node: TrieNode, in_edge: str) -> None:
    # We get the suffix link by running up the links from the
    # parent and trying to extend them. Casts are for the type
    # checker, telling them that nodes are not None
    parent = typing.cast(TrieNode, node.parent)
    if parent.is_root:
        node.suffix_link = parent
    else:
        slink = typing.cast(TrieNode, parent.suffix_link)
        while in_edge not in slink and not slink.is_root:
            slink = typing.cast(TrieNode, slink.suffix_link)
        # If we can extend, we do. Otherwise, we will
        # be in the root, and then that is what we want.
        node.suffix_link = slink[in_edge] if in_edge in slink else slink

    # The suffix link for non-roots should never be None
    assert node.suffix_link is not None

    # The out list either skips suffix_link or not, depending on
    # whether there is a label there or not. The out_list can be None.
    # We terminate the lists with a None.
    slink = node.suffix_link
    node.out_list = slink if slink.label is not None else slink.out_list


def breadth_first_trie(*strings: str) -> Trie:
    labelled = list(LS(i, SubSeq[str](x)) for i, x in enumerate(strings))

    root_lab, root_groups = group_strings(labelled)
    root = TrieNode(label=root_lab)

    queue = collections.deque[tuple[TrieNode, dict[str, list[LS]]]]()
    queue.append((root, root_groups))

    while queue:
        parent, groups = queue.popleft()
        for edge, group in groups.items():
            node_lab, node_groups = group_strings(group)
            parent.children[edge] = TrieNode(label=node_lab, parent=parent)
            queue.append((parent[edge], node_groups))
            set_suffix_link(parent[edge], edge)

    return Trie(root)


def group_strings(
    strings: list[LS]
) -> tuple[typing.Optional[int], dict[str, list[LS]]]:
    """Split input into groups according to first character.
If there is an empty string in the input, get its label.
Returns the label (or None) and the groups in a dict."""

    empty, non_empty = list[LS](), list[LS]()
    for ls in strings:
        (non_empty, empty)[len(ls.x) == 0].append(ls)

    assert(len(empty) <= 1)
    label = empty[0].label if len(empty) == 1 else None

    out_groups = collections.defaultdict[str, list[LS]](list)
    for lab, x in non_empty:
        # In the groups, slice off the first character for
        # the next level... (subseq makes this O(1)).
        out_groups[x[0]].append(LS(lab, x[1:]))

    return label, out_groups
