#!/usr/bin/env python3

import argparse
from pystr.trie import depth_first_trie


def show_trie() -> None:
    parser = argparse.ArgumentParser(
        description='Display a trie of a set of strings.')
    parser.add_argument('strings', metavar='STRING', type=str, nargs='+',
                        help='strings to build the trie of.')

    args = parser.parse_args()
    trie = depth_first_trie(*args.strings)
    print(trie.to_dot())
