#!/usr/bin/env python3

import argparse
from typing import Callable

from pystr.suffixtree import \
    SuffixTree, \
    naive_st_construction, \
    mccreight_st_construction, \
    lcp_st_construction
from pystr.lcp import lcp_from_sa
from pystr import sais

STConstructor = Callable[[str], SuffixTree]


def lcp_construction_wrapper(x: str) -> SuffixTree:
    sa = sais(x, include_sentinel=True)
    lcp = lcp_from_sa(x, sa)
    return lcp_st_construction(x, sa, lcp)


algos: dict[str, STConstructor] = {
    'naive': naive_st_construction,
    'mccreight': mccreight_st_construction,
    'lcp': lcp_construction_wrapper
}


def show_suffixtree() -> None:
    parser = argparse.ArgumentParser(
        description='Display a suffix tree.')
    parser.add_argument('x', metavar='x', type=str,
                        help='string to build the suffix tree from.')
    parser.add_argument('--algo',
                        default='mccreight',
                        nargs='?',
                        choices=algos.keys(),
                        help='construction ')

    args = parser.parse_args()
    st = algos[args.algo](args.x)
    print(st.to_dot())
