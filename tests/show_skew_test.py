import argparse
from pytest_mock import MockerFixture
from pystr_scripts import skew

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def test_show_skew(mocker: MockerFixture) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=False,
            terminal_sentinel='$',
            central_sentinel='#',
            x='mississippimmiissiissiippii')
    )
    try:
        skew.show_skew()
    except Exception:
        assert False, \
            "Something went wrong in the script"


def test_show_skew_interactive(mocker: MockerFixture) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=True,
            terminal_sentinel='$',
            central_sentinel='#',
            x='mississippimmiissiissiippii')
    )
    mocker.patch(
        'builtins.input',
        return_value=''
    )
    try:
        skew.show_skew()
    except Exception:
        assert False, \
            "Something went wrong in the script"
