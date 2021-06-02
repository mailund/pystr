import argparse
from pystr_scripts import bwt


def test_show_bwt_transition(mocker):
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
