from .suffixtree import SuffixTree, Node, Leaf, Inner

# SECTION Building lcp from suffix tree


def suf_tree_traversal(lcp: int, depth: int, n: Node,
                       sa: list[int], lcp_arr: list[int]) \
        -> tuple[list[int], list[int]]:

    # A closure might be better for this function, but creating
    # closures come at a runtime cost...

    # FIXME: This calls for pattern matching (when mypy can handle it)
    if isinstance(n, Leaf):
        sa.append(n.leaf_label)
        lcp_arr.append(lcp)
    if isinstance(n, Inner):
        depth += len(n.edge_label)
        children = [n.children[_] for _ in sorted(n.children)]
        assert children, "An inner node must have at least one child"
        # Go left with existing lcp
        suf_tree_traversal(lcp, depth,
                           children[0], sa, lcp_arr)
        # Go right with the edge as extra lcp
        for child in children[1:]:
            suf_tree_traversal(depth, depth, child,
                               sa, lcp_arr)
    return sa, lcp_arr


def sa_lcp_from_suffix_tree(st: SuffixTree) -> tuple[list[int], list[int]]:
    return suf_tree_traversal(0, 0, st.root, [], [])

# !SECTION

# SECTION Building lcp from suffix array


def inverse_sa(sa: list[int]) -> list[int]:
    isa = [0] * len(sa)
    for i, j in enumerate(sa):
        isa[j] = i
    return isa


def compare_lcp(x: str, i: int, j: int) -> int:
    m = min(len(x) - i, len(x) - j)
    for k in range(m):
        if x[i+k] != x[j+k]:
            return k
    else:
        return m


def lcp_from_sa(x: str, sa: list[int]) -> list[int]:
    lcp = [-1] * len(sa)
    isa = inverse_sa(sa)

    offset = 0
    for i in range(len(sa)):
        offset = max(0, offset - 1)
        ii = isa[i]
        if ii == 0:
            lcp[ii] = 0
            continue
        j = sa[ii - 1]
        offset += compare_lcp(x, i+offset, j+offset)
        lcp[ii] = offset

    return lcp


# !SECTION
