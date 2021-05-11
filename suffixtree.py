from __future__ import annotations
from typing import Union
from collections.abc import Iterator
from dataclasses import dataclass, field


# Using string slices is a bit wasteful of memory, because
# they hold a reference to the string, but they make the code
# easier to follow while still giving us constant time slicing.
#
# You can remove the x reference and pass the string to the
# methods instead if you want to avoid the memory waste.


@dataclass(frozen=True)
class StringSlice:
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


# You don't need separate leaf/inner classes to make a tree. I only
# do it so I can use pattern matching on nodes.


@dataclass
class Inner:
    edge_label: StringSlice
    parent: Inner | None = \
        field(default=None, repr=False)
    suffix_link: Inner | None = \
        field(default=None, repr=False)
    children: dict[str, Node] = \
        field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # Make the initial label a copy of the input, to prevent
        # modifying it in the construction algorithms.
        self.edge_label = self.edge_label[:]

    def add_children(self, *children: Iterator[Node]) -> None:
        for child in children:
            self.children[child.edge_label[0]] = child
            child.parent = self

    def __iter__(self):
        # You could make it more efficient by sorting once
        # and keeping the table sorted, but for experimenting
        # this if fine...
        for x in sorted(self.children):
            yield from self.children[x]


@dataclass
class Leaf:
    label: int
    edge_label: StringSlice
    parent: Inner | None = field(default=None, repr=False, init=False)

    def __post_init__(self):
        # Make the initial label a copy of the input, to prevent
        # modifying it in the construction algorithms.
        self.edge_label = self.edge_label[:]

    def __iter__(self):
        yield self.label


Node = Union[Inner, Leaf]


# It is a bit of overkill to use three classes to make search
# results, but it enables pattern matching, which is nice. It would
# be more efficient to simply wrap the information in the same class
# or a tuple, and you can determine the kind of result from that.
# But this makes nicer code later, because of the pattern matching
# syntax.


@dataclass
class Mismatch:
    # The destination node for the edge we mismatched on.
    n: Node
    # How far down the edge we managed to match.
    # If this is zero, it is because we couldn't get out of
    # the node
    i: int
    # The remaining search string when we started matching the edge.
    y: StringSlice


@dataclass
class Match:
    # The root of the subtree we match.
    n: Node
    # How far down the edge do we match (which of course is the
    # length of the remaining string, but still...)
    i: int
    # The remaining search string when we started matching the edge.
    y: StringSlice


SearchResult = Union[Mismatch, Match]


def tree_search(n: Node, x: StringSlice) -> SearchResult:
    # In the special case that x is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not x:
        return Match(n, 0, x)

    while True:
        if x[0] not in n.children:
            return Mismatch(n, 0, x)

        n = n.children[x[0]]
        i = match(n.edge_label, x)
        if i == len(x):
            return Match(n, i, x)
        if i < len(n.edge_label):
            return Mismatch(n, i, x)
        x = x[i:]  # Search for the remaining string

    assert False, "We should never get here"


def tree_fastsearch(n: Node, x: StringSlice) -> SearchResult:
    # In the special case that x is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not x:
        return Match(n, 0, x)

    while True:
        assert x[0] in n.children, \
            "With fast scan, there should always be an out-edge"
        n = n.children[x[0]]
        # This is the fast scan jump (instead of scanning)
        i = min(len(n.edge_label), len(x))
        if i == len(x):
            return Match(n, i, x)
        x = x[i:]  # Search for the remaining string

    assert False, "We should never get here"


def node_to_dot(n: Node, res: list[str]) -> list[str]:
    match n:
        case Leaf(label, edge_label):
            # Give the sentinel a symbol that Graphviz can display
            edge_label = str(edge_label).replace('\x00', '†')
            res.append(f'{id(n)}[label={label}, shape=circle]')
            res.append(f'{id(n.parent)} -> {id(n)}[label="{edge_label}"]')

        case Inner(edge_label, parent, suffix_link):
            if parent is None:  # Root node
                res.append(
                    f'{id(n)}[label="", shape=circle, style=filled, fillcolor=grey]'  # noqa: E501
                )
            else:
                res.append(f'{id(n)}[label="", shape=point]')
                res.append(f'{id(parent)} -> {id(n)}[label="{edge_label}"]')
            if suffix_link:
                res.append(f"{id(n)} -> {id(suffix_link)}[style=dashed]")
            for child in n.children.values():
                node_to_dot(child, res)

    return res  # Just for convinience


@dataclass
class SuffixTree:
    root: Node

    def search(self, x: str) -> Iterator[int]:
        match tree_search(self.root, StringSlice(x)):
            case Match(n):
                return iter(n)
            case _:
                return ()

    def __contains__(self, x: str):
        match tree_search(self.root, StringSlice(x)):
            case Match(_):
                return True
            case _:
                return False

    def to_dot(self) -> str:
        return "digraph {" + '\n'.join(node_to_dot(self.root, [])) + "}"


def break_edge(label: int, n: Node, j: int, y: StringSlice) -> Leaf:
    """Break the edge to node `n`, `j` characters down, adding a new leaf
with label `label` with edge `y`. Returns the new leaf."""

    new_n = Inner(n.edge_label[:j])  # Create the new node that splits the edge
    new_leaf = Leaf(label, y)        # Remaining bit of other path
    n.edge_label = n.edge_label[j:]  # Move start of n forward to remaining bit

    assert n.parent is not None      # n must have a parent here (n != root)
    n.parent.add_children(new_n)     # New node replaces n in n's parent
    new_n.add_children(n, new_leaf)  # Make n and new leaf children of of new_n

    return new_leaf


def naive_construction(s: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x = StringSlice(s + '\x00')  # Adding sentinel to the string.
    root = Inner(x[0:0])

    # Insert suffixes one at a time...
    for i in range(len(x)):
        match tree_search(root, x[i:]):
            case Mismatch(n, 0, y):
                n.add_children(Leaf(i, y))
            case Mismatch(n, j, y):
                break_edge(i, n, j, y[j:])
            case Match(_):
                # With the sentinel, we should never match completely
                assert False, "We can't match completely here"

    return SuffixTree(root)


def mccreight_construction(s: str):
    """Construct a suffix tree by searching from the root
down to the insertion point for each suffix in `s`."""

    x = StringSlice(s + '\x00')  # Adding sentinel to the string.
    root = Inner(x[0:0])
    v = Leaf(0, x)
    root.add_children(v)
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

        # If we already have a suffix link, then that is
        # the node we should slow scan from.
        if p.suffix_link:
            # y_node is the node we would get from scanning
            # through a + y, so from here we need to scan
            # for z (later in the function)
            y_node = p.suffix_link
            z = v.edge_label if p != root else x[i:]

        else:
            # Otherwise, we need to fast scan to find y_node.
            # p can't be the root here, because the root has a
            # suffix link
            pp_sl = p.parent.suffix_link
            assert pp_sl, "Parent's parent must have a suffix link"

            # Jumping to pp_sl gets us past a, so now we get y and z
            # (with the special case if p is the root) and then we are
            # ready to scan for y_node
            y = p.edge_label if p.parent is not root else p.edge_label[1:]
            z = v.edge_label

            # Fast scan to new starting point
            match tree_fastsearch(pp_sl, y):
                case Match(y_node, j, _):
                    pass
                case _:
                    assert False, "Fast scan should always find a match"

            if len(y_node.edge_label) != j:
                # We ended the search on an edge, so we can directly
                # insert the new leaf
                v = break_edge(i, y_node, j, z)
                p.suffix_link = v.parent
                continue  # Process next suffix...

            # If we landed on a node, then that is p's suffix link
            p.suffix_link = y_node

        # If we are here, we need to slow-scan, and we do that by
        # searching from y_node after the remainder of the suffix, z.
        match tree_search(y_node, z):
            case Mismatch(n, 0, w):
                v = Leaf(i, w)
                n.add_children(v)
            case Mismatch(n, j, w):
                v = break_edge(i, n, j, w[j:])
            case Match(_):
                # With the sentinel, we should never match completely
                assert False, "We can't match completely here"

    return SuffixTree(root)


if __name__ == '__main__':
    x = "missippississippi"
    st = mccreight_construction(x)
    for i in st.search("ssi"):
        print(f"ssi found at {x[i:]}")
    with open("dot.dot", "w") as f:
        print(st.to_dot(), file=f)
    for i in st.root:
        print(x[i:])
