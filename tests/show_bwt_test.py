import argparse
from pytest_mock import MockerFixture

from pystr_scripts import bwt


def test_show_bwt_transition(mocker: MockerFixture) -> None:
    x = 'mississippimmiissiissiippii'
    alpha = set(x)

    for k in range(len(x) + 1):
        for a in alpha:
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    interactive=False,
                    x=x, a=a, k=k)
            )
            bwt.show_bwt_transition()

    for k in range(len(x) + 1):
        for a in alpha:
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    interactive=True,
                    x=x, a=a, k=k)
            )
            mocker.patch(
                'builtins.input', result_value=''
            )
            bwt.show_bwt_transition()


def check_bwt_search(x: str, p: str,
                     mocker: MockerFixture) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=False,
            x=x, p=p)
    )
    bwt.show_bwt_search()

    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=True,
            x=x, p=p)
    )
    mocker.patch(
        'builtins.input', result_value=''
    )
    bwt.show_bwt_search()


def test_show_bwt_search(mocker: MockerFixture) -> None:
    x = 'mississippimmiissiissiippii'
    p = 'ssi'
    check_bwt_search(x, p, mocker)

    # Character that isn't there
    check_bwt_search(x, 'x', mocker)

    # mismatch
    check_bwt_search(x, 'ssss', mocker)
