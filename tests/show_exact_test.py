import argparse
from pystr_scripts import exact
from helpers import random_string, \
    pick_random_patterns, pick_random_patterns_len

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def run_alg(mocker, algo: str):
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        for p in pick_random_patterns(x, 10):
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    algo=algo,
                    interactive=False,
                    x=x, p=p)
            )
            exact.main()
        for p in pick_random_patterns_len(x, 10, 3):
            mocker.patch(
                'argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    algo=algo,
                    interactive=False,
                    x=x, p=p)
            )
            exact.main()


def run_alg_interactive(mocker, algo: str):
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


def test_naive(mocker):  run_alg(mocker, 'naive')
def test_border(mocker): run_alg(mocker, 'border')
def test_kmp(mocker):    run_alg(mocker, 'kmp')
def test_bmh(mocker):    run_alg(mocker, 'bmh')


def test_int_naive(mocker):  run_alg_interactive(mocker, 'naive')
def test_int_border(mocker): run_alg_interactive(mocker, 'border')
def test_int_kmp(mocker):    run_alg_interactive(mocker, 'kmp')
def test_int_bmh(mocker):    run_alg_interactive(mocker, 'bmh')
