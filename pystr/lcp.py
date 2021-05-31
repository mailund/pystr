from .suffixtree import SuffixTree, Node, Leaf, Inner
from .cols import bright_cyan, bright_green, bright_yellow, \
    bright_red, ansifree_len, green, red, underline
from .output import colour, out, place_pointers, Table, ColSpec, Align

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


# For visualisation
def sa_lcp_tbl(x: str, sa: list[int], lcp: list[int]) -> Table:
    tbl = Table(ColSpec("sa"), ColSpec("sufs"),
                ColSpec("lcp"), ColSpec("lcp_res", align=Align.RIGHT))
    for i in range(len(sa)):
        row = tbl.add_row()
        row["sa"] = f"sa[{i:>2}] ="
        if lcp[i] == -1:
            row["sufs"] = x[sa[i]:]
        else:
            row["sufs"] = colour(x[sa[i]:])[:lcp[i], underline]
        row["lcp"] = f"lcp[{i:>2}] ="
        if lcp[i] == -1:
            row["lcp_res"] = red("???")
        else:
            row["lcp_res"] = f"{lcp[i]:>2}"
    return tbl


def lcp_from_sa(x: str, sa: list[int],
                progress=False) -> list[int]:
    lcp = [-1] * len(sa)  # -1 for "unknown". Used in visualisation
    isa = inverse_sa(sa)

    offset = 0
    for i in range(len(sa)):
        offset = max(0, offset - 1)
        ii = isa[i]

        if progress:
            print()
            heading = \
                bright_cyan(f"Iteration {bright_yellow(str(i))}, ") + \
                bright_cyan(f"offset = {bright_yellow(str(offset))}")
            print(heading)
            print(bright_cyan('=' * ansifree_len(heading)))
            print()

        if ii == 0:

            if progress:
                print(bright_green(f"i={i} -> ii={ii}, lcp[0] is always 0"))
                print()

            lcp[ii] = 0
            continue

        j = sa[ii - 1]

        if progress:
            print(f"isa[{bright_yellow(str(i))}] = " +
                  f"{bright_red(str(ii))} " +
                  f" sa[{bright_red(str(ii-1))}] = " +
                  f"{bright_yellow(str(j))}")
            print()

            if offset > 0:
                out(bright_yellow(
                    place_pointers(("i", i), ("+offset", i + offset))))
            else:
                out(bright_yellow(place_pointers(("i", i))))
            out(bright_yellow(place_pointers(("v", i), ("v", i + offset))))
            out(colour(x)[i:i+offset, green][j:j+offset, green])
            out(bright_yellow(place_pointers(("^", j), ("^", j + offset))))
            if offset > 0:
                out(bright_yellow(
                    place_pointers(("j", j), ("+offset", j + offset))))
            else:
                out(bright_yellow(place_pointers(("j", j))))

            old_offset = offset

        offset += compare_lcp(x, i+offset, j+offset)
        lcp[ii] = offset

        if progress:
            print(underline("Scan result:\n"))
            out(f"sa[{isa[j]:>2}] = ",
                colour(x[j:])[:old_offset, green]
                [old_offset:offset, bright_yellow][offset, red])
            out(f"sa[{isa[i]:>2}] = ",
                colour(x[i:])[:old_offset, green]
                [old_offset:offset, bright_yellow][offset, red])
            print()
            print(bright_green(f"lcp[{ii}] == {lcp[ii]}"))
            print()
            tbl = sa_lcp_tbl(x, sa, lcp)

            # Row with the new result
            row = tbl[ii]
            row["sufs"] = colour(row["sufs"])[
                :old_offset, green & underline][
                    old_offset:offset, bright_yellow & underline][
                        offset, bright_red]
            row["lcp_res"] = bright_green(row["lcp_res"])

            if ii > 0:  # previous row
                row = tbl[ii - 1]
                row["sufs"] = colour(row["sufs"])[
                    :old_offset, green & underline][
                    old_offset:offset, bright_yellow & underline][
                        offset, bright_red]

            print(tbl)
            print()

    if progress:
        print()
        print(bright_green("DONE"))
        print()
        print(sa_lcp_tbl(x, sa, lcp))
        print()

    return lcp


# !SECTION
