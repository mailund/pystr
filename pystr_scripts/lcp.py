import argparse
from pystr import sais
from pystr.lcp import compare_lcp
from pystr_vis.cols import bright_cyan, bright_green, bright_yellow, \
    bright_red, ansifree_len, green, red, underline
from pystr_vis import colour, place_pointers, Table, ColSpec, Align


def hit_enter(interactive: bool) -> None:
    if interactive:
        input("Press ENTER to continue")


def inverse_sa(sa: list[int]) -> list[int]:
    isa = [0] * len(sa)
    for i, j in enumerate(sa):
        isa[j] = i
    return isa


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
                interactive: bool) -> list[int]:
    lcp = [-1] * len(sa)  # -1 for "unknown". Used in visualisation
    isa = inverse_sa(sa)

    offset = 0
    for i in range(len(sa)):
        offset = max(0, offset - 1)
        ii = isa[i]

        print()
        heading = \
            bright_cyan(f"Iteration {bright_yellow(str(i))}, ") + \
            bright_cyan(f"offset = {bright_yellow(str(offset))}")
        print(heading)
        print(bright_cyan('=' * ansifree_len(heading)))
        print()

        if ii == 0:

            print(bright_green(f"i={i} -> ii={ii}, lcp[0] is always 0"))
            print()
            hit_enter(interactive)
            print()

            lcp[ii] = 0
            continue

        j = sa[ii - 1]

        print(f"isa[{bright_yellow(str(i))}] = " +
              f"{bright_red(str(ii))} " +
              f" sa[{bright_red(str(ii-1))}] = " +
              f"{bright_yellow(str(j))}")
        print()

        if offset > 0:
            print(bright_yellow(
                place_pointers(("i", i), ("+offset", i + offset))),
                sep="")
        else:
            print(bright_yellow(place_pointers(("i", i))), sep="")
            print(bright_yellow(place_pointers(
                ("v", i), ("v", i + offset))), sep="")
        print(colour(x)[i:i+offset, green][j:j+offset, green], sep="")
        print(bright_yellow(place_pointers(
            ("^", j), ("^", j + offset))), sep="")
        if offset > 0:
            print(bright_yellow(
                place_pointers(("j", j), ("+offset", j + offset))), sep="")
        else:
            print(bright_yellow(place_pointers(("j", j))), sep="")

        old_offset = offset

        print()
        hit_enter(interactive)
        print()

        offset += compare_lcp(x, i+offset, j+offset)
        lcp[ii] = offset

        print(underline("Scan result:\n"))
        print(f"sa[{isa[j]:>2}] = ",
              colour(x[j:])[:old_offset, green]
              [old_offset:offset, bright_yellow][offset, red],
              sep="")
        print(f"sa[{isa[i]:>2}] = ",
              colour(x[i:])[:old_offset, green]
              [old_offset:offset, bright_yellow][offset, red],
              sep="")
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
        hit_enter(interactive)

    print()
    print(bright_green("DONE"))
    print()
    print(sa_lcp_tbl(x, sa, lcp))
    print()

    return lcp


def show_lcp_sa() -> None:
    parser = argparse.ArgumentParser(
        description='Display run of algorithm for constructing the lcp from the sa.')    # noqa: E501

    parser.add_argument('-i', '--interactive',
                        dest='interactive', action='store_true',
                        help='the visualisation should pause between steps (default).')  # noqa: E501
    parser.add_argument('-n', '--not-interactive',
                        dest='interactive', action='store_false',
                        help='the visualisation should not pause between steps.')        # noqa: E501
    parser.set_defaults(interactive=True)
    parser.add_argument('x', metavar='x', type=str,
                        help='string to build the sa/lcp from.')

    args = parser.parse_args()
    sa = sais.sais(args.x)
    lcp_from_sa(args.x, sa, args.interactive)
