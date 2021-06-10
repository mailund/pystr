import argparse
from pytest_mock import MockerFixture

from pystr_scripts import exact
from helpers import random_string, \
    pick_random_patterns, pick_random_patterns_len

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def run_alg(mocker: MockerFixture, algo: str) -> None:
    for _ in range(10):
        x = random_string(20, alpha="abcd")
        for p in pick_random_patterns(x, 10):
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    algo=algo,
                    interactive=False,
                    x=x, p=p)
            )
            exact.main()
        for p in pick_random_patterns_len(x, 5, 3):
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    algo=algo,
                    interactive=False,
                    x=x, p=p)
            )
            exact.main()


def run_alg_interactive(mocker: MockerFixture, algo: str) -> None:
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            algo=algo,
            interactive=True,
            x='mississippimmiissiippii', p='ssi')
    )
    mocker.patch(
        'builtins.input',
        return_value=''
    )

    exact.main()


def test_naive(mocker: MockerFixture) -> None:
    run_alg(mocker, 'naive')


def test_border(mocker: MockerFixture) -> None:
    run_alg(mocker, 'border')


def test_kmp(mocker: MockerFixture) -> None:
    run_alg(mocker, 'kmp')


def test_bmh(mocker: MockerFixture) -> None:
    run_alg(mocker, 'bmh')


def test_int_naive(mocker: MockerFixture) -> None:
    run_alg_interactive(mocker, 'naive')


def test_int_border(mocker: MockerFixture) -> None:
    run_alg_interactive(mocker, 'border')


def test_int_kmp(mocker: MockerFixture) -> None:
    run_alg_interactive(mocker, 'kmp')


def test_int_bmh(mocker: MockerFixture) -> None:
    run_alg_interactive(mocker, 'bmh')
