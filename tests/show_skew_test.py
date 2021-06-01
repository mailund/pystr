import argparse
from pystr_scripts import skew

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def test_show_skew(mocker):
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=False,
            terminal_sentinel='$',
            central_sentinel='#',
            x='mississippi')
    )
    try:
        skew.show_skew()
    except Exception:
        assert False, \
            "Something went wrong in the script"
