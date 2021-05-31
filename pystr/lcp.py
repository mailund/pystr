from .suffixtree import SuffixTree, Node, Leaf, Inner


# A closure might be better for this function, but creating
# closures come at a runtime cost...
def suf_tree_traversal(lcp: int, n: Node,
                       sa: list[int], lcp_arr: list[int]) \
        -> tuple[list[int], list[int]]:

    # FIXME: This calls for pattern matching (when mypy can handle it)
    if isinstance(n, Leaf):
        sa.append(n.leaf_label)
        lcp_arr.append(lcp)
    if isinstance(n, Inner):
        children = [n.children[_] for _ in sorted(n.children)]
        assert children, "An inner node must have at least one child"
        suf_tree_traversal(lcp, children[0], sa, lcp_arr)
        for child in children[1:]:
            suf_tree_traversal(lcp+len(n.edge_label), child, sa, lcp_arr)
    return sa, lcp_arr


def sa_lcp_from_suffix_tree(st: SuffixTree) -> tuple[list[int], list[int]]:
    return suf_tree_traversal(0, st.root, [], [])
