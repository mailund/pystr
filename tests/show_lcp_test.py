import argparse
from pytest_mock import MockerFixture

from pystr_scripts import lcp
from helpers import random_string

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def test_show_lcp(mocker: MockerFixture) -> None:
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        mocker.patch(
            'argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                interactive=False,
                x=x)
        )
        lcp.show_lcp_sa()


def test_show_lcp_interactive(mocker: MockerFixture) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=True,
            x='mississippi')
    )
    mocker.patch(
        'builtins.input',
        return_value=''
    )
    lcp.show_lcp_sa()
