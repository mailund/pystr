"""Constructing and using suffix trees."""

from __future__ import annotations

import dataclasses
import typing

from .alphabet import Alphabet
from .subseq import SubSeq

# SECTION Suffix Tree representation

# You don't need separate leaf/inner classes, but you get a little
# type checking if you have them. You also save a little space by
# not having all the attributes in a combined class.


@dataclasses.dataclass
class Node:  # Should be abc ABC, but doesn't work with type checker
    """
    Representation of a node in a suffix tree.

    This is an abstract class. Concrete nodes are either Inner of Leaf.
    """

    edge_label: SubSeq[int]  # slice of underlying bytearray
    parent: typing.Optional[Inner] = \
        dataclasses.field(default=None, init=False, repr=False)

    # These methods are only here for the type checker.
    # They will never be used because we never have Node objects.
    def __iter__(self) -> typing.Iterator[int]:  # noqa: pylint: disable=non-iterator-returned
        """Iterate through all the leaves in the tree rooted in this node."""
        ...  # pragma no cover

    def to_dot(self, _: Alphabet) -> typing.Iterator[str]:  # noqa: no-self-use, pylint: disable=no-self-use
        """Represent the tree rooted in this node as dot."""
        ...  # pragma no cover


@dataclasses.dataclass
class Inner(Node):
    """An inner node."""

    suffix_link: typing.Optional[Inner] = \
        dataclasses.field(default=None, init=False, repr=False)
    children: dict[int, Node] = \
        dataclasses.field(default_factory=dict, init=False, repr=False)

    def add_children(self, *children: Node) -> None:
        """Add children to this inner node."""
        for child in children:
            self.children[child.edge_label[0]] = child
            child.parent = self

    def out_child(self, edge: SubSeq[int]) -> Node:
        """Find the child we go to if we follow the first letter in edge."""
        return self.children[edge[0]]

    def to_dot(self, alpha: Alphabet) -> typing.Iterator[str]:
        """Get a dot representation for the tree rooted here."""
        if self.parent is None:  # Root node
            yield f'{id(self)}[label="", shape=circle, style=filled, fillcolor=grey]'  # noqa: E501
        else:
            elab = alpha.revmap(self.edge_label)
            yield f'{id(self)}[label="", shape=point]'
            yield f'{id(self.parent)} -> {id(self)}[label="{elab}"]'
        if self.suffix_link:
            yield f"{id(self)} -> {id(self.suffix_link)}[style=dashed, color=red]"  # noqa
        for child in self.children.values():
            yield from child.to_dot(alpha)

    def __iter__(self) -> typing.Iterator[int]:
        """Iterate through all leaves in the tree rooted here."""
        # You could make it more efficient by sorting once
        # and keeping the table sorted, but for experimenting
        # this if fine...
        for x in sorted(self.children):
            yield from self.children[x]

    def __eq__(self, other: object) -> bool:
        """Test if two nodes are equivalent."""
        if not isinstance(other, Inner):  # pragma: no cover
            return False
        assert isinstance(other, Inner)  # For the type checker

        if self.edge_label != other.edge_label:
            return False

        # Equal if sorted children are equal.
        my_children = list(sorted(self.children.items()))
        others_children = list(sorted(other.children.items()))
        if len(my_children) != len(others_children):
            return False
        return all(
            a == b for a, b
            in zip(my_children, others_children)
        )


@dataclasses.dataclass(init=False)
class Leaf(Node):
    """A leaf in a suffix tree."""

    leaf_label: int

    # Explicit __init__ because I prefer to have the
    # leaf_label before the edge_label
    def __init__(self, leaf_label: int, edge_label: SubSeq[int]):
        """Create a leaf."""
        super().__init__(edge_label)
        self.leaf_label = leaf_label

    def to_dot(self, alpha: Alphabet) -> typing.Iterator[str]:
        """Get the dot representation of the leaf."""
        lab = alpha.revmap(self.edge_label)
        yield f'{id(self)}[label={self.leaf_label}, shape=circle]'
        yield f'{id(self.parent)} -> {id(self)}[label="{lab}"]'

    def __iter__(self) -> typing.Iterator[int]:
        """Iterate through all the leaves rooted in this node."""
        yield self.leaf_label

    def __eq__(self, other: object) -> bool:
        """Test if two nodes are equivalent."""
        if not isinstance(other, Leaf):  # pragma: no cover
            return False
        return self.edge_label == other.edge_label and \
            self.leaf_label == other.leaf_label


@ dataclasses.dataclass
class SuffixTree:
    """A suffix tree."""

    alpha: Alphabet
    root: Inner

    def search(self, p: str) -> typing.Iterator[int]:
        """Find all occurences of p in the suffix tree."""
        try:
            p_ = SubSeq[int](self.alpha.map(p))
        except KeyError:
            # when we can't map, we don't get hits
            return

        n, j, y = tree_search(self.root, p_)
        if j == len(y):
            # We search all the way through the last string,
            # so we have a match
            yield from iter(n)

    def __contains__(self, p: str) -> bool:
        """Test if string p is in the tree."""
        try:
            p_ = SubSeq[int](self.alpha.map(p))
        except KeyError:
            # when we can't map, we don't get hits
            return False

        _, j, y = tree_search(self.root, p_)
        return j == len(y)

    def to_dot(self) -> str:
        """Get a dot representation of a tree."""
        return "digraph { rankdir=\"LR\" " + '\n'.join(self.root.to_dot(self.alpha)) + "}"  # noqa

    def __eq__(self, other: object) -> bool:
        """Test if two trees are equivalent."""
        if not isinstance(other, SuffixTree):  # pragma: no cover
            return False
        return self.root == other.root

# !SECTION

# SECTION Searching in a suffix tree


def first_mismatch(x: SubSeq[int], y: SubSeq[int]) -> int:
    """
    Return how far along x and y we can match.

    Return index of first mismatch.
    """
    i = -1  # Handle special case with empty string
    for i, (a, b) in enumerate(zip(x, y)):
        if a != b:
            return i
    return i + 1  # matched all the way through


# FIXME: I think this would be nicer with classes and pattern matching...
SearchResult = tuple[Node, int, SubSeq[int]]
# This is the node we last searched on, how far down
# the edge we got (or zero if we couldn't leave the
# node), and the last string we searched.


def tree_search(n: Inner, p: SubSeq[int]) -> SearchResult:
    """Search for p down the tree rooted in n."""
    # In the special case that p is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not p:
        return n, 0, p

    while True:
        if p[0] not in n.children:
            return n, 0, p

        child = n.out_child(p)
        i = first_mismatch(child.edge_label, p)
        if i == len(p) or i < len(child.edge_label):
            return child, i, p

        assert isinstance(child, Inner), \
            "We can only continue searching from an inner node"
        n, p = child, p[i:]


def tree_fastsearch(n: Inner, p: SubSeq[int]) -> SearchResult:
    """Do a fast scan after p starting at n."""
    # In the special case that x is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not p:
        return n, 0, p
    while True:
        assert p[0] in n.children, \
            "With fast scan, there should always be an out-edge"
        child = n.out_child(p)
        # This is the fast scan jump (instead of scanning)
        i = min(len(child.edge_label), len(p))
        if i == len(p):
            return child, i, p

        assert isinstance(child, Inner), \
            "We can only continue searching from an inner node"
        n, p = child, p[i:]

    assert False, "We should never get here"


def break_edge(leaf_label: int, n: Node, k: int, z: SubSeq[int]) -> Leaf:
    """
    Break an edge in two.

    Break the edge to node `n`, `k` characters down, adding a new leaf
    with label `label` with edge `z`. Returns the new leaf.
    """
    new_n = Inner(n.edge_label[:k])  # The node that splits the edge
    new_leaf = Leaf(leaf_label, z)   # Remaining bit of other path
    n.edge_label = n.edge_label[k:]  # Move start of n forward

    assert n.parent is not None      # n must have a parent (n != root)
    n.parent.add_children(new_n)     # New node replaces n in n's parent
    new_n.add_children(n, new_leaf)  # Make n and new leaf children of new

    return new_leaf


# !SECTION

# SECTION Naive construction algorithm

def naive_st_construction(s: str) -> SuffixTree:
    """
    Naive construction algorithm.

    Construct a suffix tree by searching from the root
    down to the insertion point for each suffix in `s`.
    """
    x_, alpha = Alphabet.mapped_string_with_sentinel(s)
    x = SubSeq[int](x_)
    root = Inner(x[0:0])

    # Insert suffixes one at a time...
    for i in range(len(x)):
        n, j, y = tree_search(root, x[i:])
        if j == 0:
            # We couldn't get out of the node
            assert isinstance(n, Inner), \
                "If we can't get out of a node, it is an inner node."
            n.add_children(Leaf(i, y))
        elif j < len(y):
            # We had a mismatch on the edge
            break_edge(i, n, j, y[j:])
        else:  # pragma: no cover
            # With the sentinel, we should never match completely
            assert False, "We can't match completely here"

    return SuffixTree(alpha, root)

# !SECTION

# SECTION McCreights construction algorithm


def mccreight_st_construction(s: str) -> SuffixTree:
    """
    Construct a suffix tree with McCreight's algorithm.

    Construct a suffix tree by searching from the root
    down to the insertion point for each suffix in `s`,
    but exploiting suffix links and fast scan along the way.
    """
    x_, alpha = Alphabet.mapped_string_with_sentinel(s)
    x = SubSeq[int](x_)
    root = Inner(x[0:0])
    v = Leaf(0, x)
    root.add_children(v)
    root.suffix_link = root

    # Insert suffixes one at a time...
    for i in range(1, len(x)):
        # Idea: split x[i:] into y+z+w where we jump
        # past y, then fast-scan through z, and then
        # slow-scan through w.
        # In the general case, y is the suffix of the path
        # down to v.parent.parent, z is the label on
        # v.parent and w is the label on v. There's
        # just some special cases to deal with it...

        p = v.parent
        assert p is not None, "A leaf should always have a parent"

        # If we already have a suffix link, then that is
        # the node we should slow scan from.
        if p.suffix_link is not None:
            # z_node is the node we would get from scanning
            # through y + z, so from here we need to scan
            # for z (later in the function)
            z_node = p.suffix_link
            w = v.edge_label if p is not root else x[i:]

        else:
            # Otherwise, we need to fast scan to find z_node.
            # p can't be the root here, because the root has a
            # suffix link
            assert p.parent is not None, "p can't be the root."
            assert p.parent.suffix_link, \
                "Parent's parent must have a suffix link"

            # Jumping to pp.suffix_link gets us past a, so now we get z and w
            # (with the special case if p is the root) and then we are
            # ready to scan for z_node
            z = p.edge_label if p.parent is not root else p.edge_label[1:]
            w = v.edge_label

            # Fast scan to new starting point
            n, j, z_res = tree_fastsearch(p.parent.suffix_link, z)
            assert j == len(z_res), "Fast scan should always find a match"
            z_node = typing.cast(Inner, n)  # For type checker...

            if len(z_node.edge_label) != j:
                # We ended the search on an edge, so we can directly
                # insert the new leaf
                v = break_edge(i, z_node, j, w)
                p.suffix_link = v.parent
                continue  # Process next suffix...

            # The result was on a node, and we continue from there
            # (using two variables make the type checker happier).
            assert isinstance(z_node, Inner), \
                "A mismatch on a node means that it is an inner node."
            # If we landed on a node, then that is p's suffix link
            p.suffix_link = z_node

        # If we are here, we need to slow-scan, and we do that by
        # searching from y_node after the remainder of the suffix, z.
        n, j, w_res = tree_search(z_node, w)
        assert j != len(w_res), "We can't match completely here."
        if j == 0:
            # Mismatch on a node...
            assert isinstance(n, Inner), \
                "Mismatch on a node must be on an inner node."
            v = Leaf(i, w_res)
            n.add_children(v)
        elif j < len(w_res):
            # Mismatch on an edge
            v = break_edge(i, n, j, w_res[j:])

    return SuffixTree(alpha, root)

# !SECTION

# SECTION LCP construction algorithm


def search_up(n: Node, length: int) -> tuple[Node, int]:
    """Move length up the tree starting at node n."""
    while length and len(n.edge_label) <= length:
        assert n.parent is not None  # This is mostly for the type checker...
        length -= len(n.edge_label)
        n = n.parent
    # Depth down the edge depends on whether we reached
    depth = 0 if length == 0 else len(n.edge_label) - length
    return n, depth


def lcp_st_construction(s: str, sa: list[int], lcp: list[int]) -> SuffixTree:
    """Construct a suffix tree from the suffix and lcp arrays."""
    x_, alpha = Alphabet.mapped_string_with_sentinel(s)
    x = SubSeq[int](x_)
    root = Inner(x[0:0])
    v = Leaf(sa[0], x[sa[0]:])
    root.add_children(v)

    for i in range(1, len(sa)):
        n, depth = search_up(v, len(x) - sa[i - 1] - lcp[i])
        if depth == 0:
            # It is, but the type checker doesn't know yet...
            assert isinstance(n, Inner)

            v = Leaf(sa[i], x[sa[i] + lcp[i]:])
            n.add_children(v)
        else:
            v = break_edge(sa[i], n, depth, x[sa[i] + lcp[i]:])

    return SuffixTree(alpha, root)

# !SECTION
