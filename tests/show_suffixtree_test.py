import argparse
from pytest_mock import MockerFixture
from pystr_scripts import suffixtree

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def test_show_trie(mocker: MockerFixture) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            x='mississippi')
    )
    suffixtree.show_suffixtree()
