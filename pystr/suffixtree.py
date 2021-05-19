from __future__ import annotations
from collections.abc import Iterator, Iterable
from dataclasses import dataclass, field
from typing import Optional
from .subseq import substr


# You don't need separate leaf/inner classes, but you get a little
# type checking if you have them. You also save a little space by
# not having all the attributes in a combined class.


@dataclass
class Node:  # Should be abc ABC, but doesn't work with type checker
    edge_label: substr  # Gives me constant time slicing
    parent: Optional[Inner] = \
        field(default=None, init=False, repr=False)

    # These methods are only here for the type checker.
    # They will never be used because we never have Node objects.
    def __iter__(self) -> Iterator[int]: ...
    def to_dot(self, res: list[str]) -> list[str]: ...


@dataclass
class Inner(Node):
    suffix_link: Optional[Inner] = \
        field(default=None, init=False, repr=False)
    children: dict[str, Node] = \
        field(default_factory=dict, init=False, repr=False)

    def add_children(self, *children: Node) -> None:
        for child in children:
            self.children[child.edge_label[0]] = child
            child.parent = self

    def out_child(self, edge: str | substr) -> Node:
        return self.children[edge[0]]

    def to_dot(self, res: list[str]) -> list[str]:
        if self.parent is None:  # Root node
            res.append(
                f'{id(self)}[label="", shape=circle, style=filled, fillcolor=grey]'  # noqa: E501
            )
        else:
            el = self.edge_label
            res.append(f'{id(self)}[label="", shape=point]')
            res.append(f'{id(self.parent)} -> {id(self)}[label="{el}"]')
        if self.suffix_link:
            res.append(f"{id(self)} -> {id(self.suffix_link)}[style=dashed]")
        for child in self.children.values():
            child.to_dot(res)

        return res  # Just for convinience

    def __iter__(self) -> Iterator[int]:
        # You could make it more efficient by sorting once
        # and keeping the table sorted, but for experimenting
        # this if fine...
        for x in sorted(self.children):
            yield from self.children[x]


@dataclass(init=False)
class Leaf(Node):
    leaf_label: int

    # Explicit __init__ because I prefer to have the
    # leaf_label before the edge_label
    def __init__(self, leaf_label: int, edge_label: substr):
        super().__init__(edge_label)
        self.leaf_label = leaf_label

    def to_dot(self, res: list[str]) -> list[str]:
        # Give the sentinel a symbol that Graphviz can display
        edge_label = str(self.edge_label).replace('\x00', '†')
        res.append(f'{id(self)}[label={self.leaf_label}, shape=circle]')
        res.append(f'{id(self.parent)} -> {id(self)}[label="{edge_label}"]')
        return res

    def __iter__(self) -> Iterator[int]:
        yield self.leaf_label


def first_mismatch(x: Iterable[str], y: Iterable[str]) -> int:
    """Returns how far along x and y we can match.
Return index of first mismatch."""
    i = -1  # Handle special case with empty string
    for i, (a, b) in enumerate(zip(x, y)):
        if a != b:
            return i
    return i + 1  # matched all the way through


SearchResult = tuple[Node, int, substr]
# This is the node we last searched on, how far down
# the edge we got (or zero if we couldn't leave the
# node), and the last string we searched.


def tree_search(n: Inner, p: substr) -> SearchResult:
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


def tree_fastsearch(n: Inner, p: substr) -> SearchResult:
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


@dataclass
class SuffixTree:
    root: Inner

    def search(self, p: str) -> Iterator[int]:
        n, j, y = tree_search(self.root, substr(p))
        if j == len(y):
            # We search all the way through the last string,
            # so we have a match
            return iter(n)
        else:
            return iter(())

    def __contains__(self, p: str):
        _, j, y = tree_search(self.root, substr(p))
        return j == len(y)

    def to_dot(self) -> str:
        return "digraph {" + '\n'.join(self.root.to_dot([])) + "}"


def break_edge(leaf_label: int, n: Node, k: int, z: substr) -> Leaf:
    """Break the edge to node `n`, `k` characters down, adding a new leaf
with label `label` with edge `z`. Returns the new leaf."""

    new_n = Inner(n.edge_label[:k])  # The node that splits the edge
    new_leaf = Leaf(leaf_label, z)   # Remaining bit of other path
    n.edge_label = n.edge_label[k:]  # Move start of n forward

    assert n.parent is not None      # n must have a parent (n != root)
    n.parent.add_children(new_n)     # New node replaces n in n's parent
    new_n.add_children(n, new_leaf)  # Make n and new leaf children of new

    return new_leaf


def naive_st_construction(s: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x = substr(s + '\x00')  # Adding sentinel to the string.
    root = Inner(x[0:0])

    # Insert suffixes one at a time...
    # I leave out the last suffix, the sentinel, since it is
    # just an artefact of the algorithm and we practically
    # never want it...
    for i in range(len(x) - 1):
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

    return SuffixTree(root)


def mccreight_st_construction(s: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x = substr(s + '\x00')  # Adding sentinel to the string
    root = Inner(x[0:0])
    v = Leaf(0, x)
    root.add_children(v)
    root.suffix_link = root

    # Insert suffixes one at a time...
    # I leave out the last suffix, the sentinel, since it is
    # just an artefact of the algorithm and we practically
    # never want it...
    for i in range(1, len(x) - 1):
        # Idea: split x[i:] into a+y+z where we jump
        # past a, then fast-scan through y, and then
        # slow-scan through z.
        # In the general case, a is the suffix of the path
        # down to v.parent.parent, y is the label on
        # v.parent and z is the label on v. There's
        # just some special cases to deal with it...

        p = v.parent
        assert p is not None, "A leaf should always have a parent"

        # If we already have a suffix link, then that is
        # the node we should slow scan from.
        if p.suffix_link is not None:
            # y_node is the node we would get from scanning
            # through a + y, so from here we need to scan
            # for z (later in the function)
            y_node = p.suffix_link
            z = v.edge_label if p != root else x[i:]

        else:
            # Otherwise, we need to fast scan to find y_node.
            # p can't be the root here, because the root has a
            # suffix link
            assert p.parent is not None, "p can't be the root."
            pp = p.parent
            assert pp.suffix_link, "Parent's parent must have a suffix link"

            # Jumping to pp.suffix_link gets us past a, so now we get y and z
            # (with the special case if p is the root) and then we are
            # ready to scan for y_node
            y = p.edge_label if p.parent is not root else p.edge_label[1:]
            z = v.edge_label

            # Fast scan to new starting point
            y_res, j, w = tree_fastsearch(pp.suffix_link, y)
            assert j == len(w), "Fast scan should always find a match"

            if len(y_res.edge_label) != j:
                # We ended the search on an edge, so we can directly
                # insert the new leaf
                v = break_edge(i, y_res, j, z)
                p.suffix_link = v.parent
                continue  # Process next suffix...
            else:
                # The result was on a node, and we continue from there
                # (using two variables make the type checker happier).
                assert isinstance(y_res, Inner), \
                    "A mismatch on a node means that it is an inner node."
                y_node = y_res

            # If we landed on a node, then that is p's suffix link
            p.suffix_link = y_node

        # If we are here, we need to slow-scan, and we do that by
        # searching from y_node after the remainder of the suffix, z.
        n, j, w = tree_search(y_node, z)
        assert j != len(w), "We can't match completely here."
        if j == 0:
            # Mismatch on a node...
            assert isinstance(n, Inner), \
                "Mismatch on a node must be on an inner node."
            v = Leaf(i, w)
            n.add_children(v)
        elif j < len(w):
            # Mismatch on an edge
            v = break_edge(i, n, j, w[j:])

    return SuffixTree(root)
