import argparse
from pystr_scripts import exact

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def run_alg(mocker, algo: str):
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            algo=algo,
            interactive=False,
            x='mississippi', p='ssi')
    )
    exact.main()


def test_naive(mocker):  run_alg(mocker, 'naive')
def test_border(mocker): run_alg(mocker, 'border')
def test_kmp(mocker):    run_alg(mocker, 'kmp')
def test_bmh(mocker):    run_alg(mocker, 'bmh')
