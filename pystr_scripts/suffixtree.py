#!/usr/bin/env python3

import argparse
from pystr.suffixtree import mccreight_st_construction


def show_suffixtree() -> None:
    parser = argparse.ArgumentParser(
        description='Display a trie of a set of strings.')
    parser.add_argument('x', metavar='STRING', type=str,
                        help='string to build the suffix tree from.')

    args = parser.parse_args()
    st = mccreight_st_construction(args.x)
    print(st.to_dot())
