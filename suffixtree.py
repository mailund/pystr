from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import overload


@dataclass(frozen=True)
class StringSlice:
    """This is a wrapper around strings that lets me slice in constant time.
It is helpful in places to be able to write code as if we are manipulating
strings rather than pairs of indices."""
    x: str
    i: int = 0
    j: int = -1

    def __post_init__(self) -> None:
        if self.j == -1:
            # Hack around frozen to get a default j that depends
            # on the length of x.
            object.__setattr__(self, "j", len(self.x))

        assert self.i <= self.j, "Start must come before end."
        # The legal range for indices is zero to
        # the length of the string. Notice that this
        # allows indices one beyond the last character.
        # That is usually how an end-index matches the
        # end of the string, but to handle empty strings
        # we allow it for the start index as well.
        assert 0 <= self.i <= len(self.x), \
            "Slices must be within the string's range."
        assert 0 <= self.j <= len(self.x), \
            "Slices must be within the string's range."

    # These are needed to inform the type checker about the
    # two different return types for indexing/slicing.
    @overload
    def __getitem__(self, _: int) -> str: ...
    @overload
    def __getitem__(self, _: slice) -> StringSlice: ...

    def __getitem__(self, i) -> str | StringSlice:
        if isinstance(i, slice):
            start = i.start if i.start is not None else 0
            stop = i.stop if i.stop is not None else len(self)
            return StringSlice(self.x, self.i + start, self.i + stop)
        else:
            return self.x[self.i + i]

    def __str__(self) -> str:
        return self.x[self.i:self.j]
    __repr__ = __str__

    def __iter__(self) -> Iterator[str]:
        return (self.x[i] for i in range(self.i, self.j))

    def __len__(self) -> int:
        return self.j - self.i

    def __bool__(self) -> bool:
        return self.i < self.j


def match(x: StringSlice | str, y: StringSlice | str) -> int:
    """Returns how far along x and y we can match.
Return index of first mismatch."""
    i = -1  # Handle special case with empty string
    for i in range(min(len(x), len(y))):
        if x[i] != y[i]:
            return i
    return i + 1  # matched all the way through


# You don't need separate leaf/inner classes, but you get a little
# type checking if you have them. You also save a little space by
# not having all the attributes in a combined class.


@dataclass
class Node:  # Should be abc ABC, but doesn't work with dataclass
    i: int
    j: int
    parent: Inner | None = \
        field(default=None, repr=False, init=False)

    def edge_label(self, x: str) -> StringSlice:
        return StringSlice(x, self.i, self.j)

    def __iter__(self) -> Iterator[int]:
        pass

    def to_dot(self, x: str, res: list[str]) -> list[str]:
        return []


@dataclass
class Inner(Node):
    suffix_link: Inner | None = \
        field(default=None, init=False, repr=False)
    children: dict[str, Node] = \
        field(default_factory=dict, init=False, repr=False)

    def add_children(self, x: str, *children: Node) -> None:
        for child in children:
            self.children[x[child.i]] = child
            child.parent = self

    def out_child(self, edge: str | StringSlice) -> Node:
        return self.children[edge[0]]

    def to_dot(self, x: str, res: list[str]) -> list[str]:
        if self.parent is None:  # Root node
            res.append(
                f'{id(self)}[label="", shape=circle, style=filled, fillcolor=grey]'  # noqa: E501
            )
        else:
            el = self.edge_label(x)
            res.append(f'{id(self)}[label="", shape=point]')
            res.append(f'{id(self.parent)} -> {id(self)}[label="{el}"]')
        if self.suffix_link:
            res.append(f"{id(self)} -> {id(self.suffix_link)}[style=dashed]")
        for child in self.children.values():
            child.to_dot(x, res)

        return res  # Just for convinience

    def __iter__(self) -> Iterator[int]:
        # You could make it more efficient by sorting once
        # and keeping the table sorted, but for experimenting
        # this if fine...
        for x in sorted(self.children):
            yield from self.children[x]


@dataclass
class Leaf(Node):
    label: int

    def to_dot(self, x: str, res: list[str]) -> list[str]:
        # Give the sentinel a symbol that Graphviz can display
        edge_label = str(self.edge_label(x)).replace('\x00', '†')
        res.append(f'{id(self)}[label={self.label}, shape=circle]')
        res.append(f'{id(self.parent)} -> {id(self)}[label="{edge_label}"]')
        return res

    def __iter__(self) -> Iterator[int]:
        yield self.label


SearchResult = tuple[Node, int, StringSlice]
# This is the node we last searched on, how far down
# the edge we got (or zero if we couldn't leave the
# node), and the last string we searched.


def tree_search(n: Inner, x: str, p: StringSlice) -> SearchResult:
    # In the special case that p is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not p:
        return n, 0, p

    while True:
        if p[0] not in n.children:
            return n, 0, p

        child = n.out_child(p)
        i = match(child.edge_label(x), p)
        if i == len(p) or i < len(child.edge_label(x)):
            return child, i, p

        assert isinstance(child, Inner), \
            "We can only continue searching from an inner node"
        n, p = child, p[i:]


def tree_fastsearch(n: Inner, x: str, p: StringSlice) -> SearchResult:
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
        i = min(len(child.edge_label(x)), len(p))
        if i == len(p):
            return child, i, p

        assert isinstance(child, Inner), \
            "We can only continue searching from an inner node"
        n, p = child, p[i:]

    assert False, "We should never get here"


@dataclass
class SuffixTree:
    x: str
    root: Inner

    def search(self, p: str) -> Iterator[int]:
        n, j, y = tree_search(self.root, self.x, StringSlice(p))
        if j == len(y):
            # We search all the way through the last string,
            # so we have a match
            return iter(n)
        else:
            return iter(())

    def __contains__(self, p: str):
        n, j, y = tree_search(self.root, self.x, StringSlice(p))
        return j == len(y)

    def to_dot(self) -> str:
        return "digraph {" + \
            '\n'.join(self.root.to_dot(self.x, [])) + \
            "}"


def break_edge(label: int, n: Node, k: int, z: StringSlice) -> Leaf:
    """Break the edge to node `n`, `k` characters down, adding a new leaf
with label `label` with edge [`i`,`j`]. Returns the new leaf."""

    new_n = Inner(n.i, n.i+k)             # The node that splits the edge
    new_leaf = Leaf(z.i, z.j, label)      # Remaining bit of other path
    n.i += k                              # Move start of n forward

    assert n.parent is not None           # n must have a parent (n != root)
    n.parent.add_children(z.x, new_n)     # New node replaces n in n's parent
    new_n.add_children(z.x, n, new_leaf)  # Make n and new leaf children of new

    return new_leaf


def naive_construction(x: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x += '\x00'  # Adding sentinel to the string.
    root = Inner(0, 0)

    # Insert suffixes one at a time...
    for i in range(len(x)):
        n, j, y = tree_search(root, x, StringSlice(x, i))
        if j == 0:
            # We couldn't get out of the node
            assert isinstance(n, Inner), \
                "If we can't get out of a node, it is an inner node."
            n.add_children(x, Leaf(y.i, y.j, i))
        elif j < len(y):
            # We had a mismatch on the edge
            break_edge(i, n, j, y[j:])
        else:
            # With the sentinel, we should never match completely
            assert False, "We can't match completely here"

    return SuffixTree(x, root)


def mccreight_construction(x: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x += '\x00'  # Adding sentinel to the string.
    root = Inner(0, 0)
    v = Leaf(0, len(x), 0)
    root.add_children(x, v)
    root.suffix_link = root

    # Insert suffixes one at a time...
    for i in range(1, len(x)):
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
            z = v.edge_label(x) if p != root else StringSlice(x, i)

        else:
            # Otherwise, we need to fast scan to find y_node.
            # p can't be the root here, because the root has a
            # suffix link
            assert p.parent is not None, "p can't be the root."
            pp_sl = p.parent.suffix_link
            assert pp_sl, "Parent's parent must have a suffix link"

            # Jumping to pp_sl gets us past a, so now we get y and z
            # (with the special case if p is the root) and then we are
            # ready to scan for y_node
            pel = p.edge_label(x)
            y = pel if p.parent is not root else pel[1:]
            z = v.edge_label(x)

            # Fast scan to new starting point
            y_res, j, w = tree_fastsearch(pp_sl, x, y)
            assert j == len(w), "Fast scan should always find a match"

            if len(y_res.edge_label(x)) != j:
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
        n, j, w = tree_search(y_node, x, z)
        assert j != len(w), "We can't match completely here."
        if j == 0:
            # Mismatch on a node...
            assert isinstance(n, Inner), \
                "Mismatch on a node must be on an inner node."
            v = Leaf(w.i, w.j, i)
            n.add_children(x, v)
        elif j < len(w):
            # Mismatch on an edge
            v = break_edge(i, n, j, w[j:])

    return SuffixTree(x, root)


if __name__ == '__main__':
    x = "missippississippi"

    print("Naive:")
    st = naive_construction(x)
    for i in st.search("ssi"):
        print(f"ssi found at {x[i:]}")
    with open("naive-dot.dot", "w") as f:
        print(st.to_dot(), file=f)
    for i in st.root:
        print(x[i:])
    print()

    print("McCreight:")
    st = mccreight_construction(x)
    for i in st.search("ssi"):
        print(f"ssi found at {x[i:]}")
    with open("mccreight-dot.dot", "w") as f:
        print(st.to_dot(), file=f)
    for i in st.root:
        print(x[i:])
    print()
