import argparse
from pystr_scripts import lcp

# This is really just a call... I don't know
# how to check that the arguments are correct when
# it will accept any string arguments..


def test_show_lcp(mocker):
    mocker.patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            interactive=False,
            x='mississippi')
    )
    lcp.show_lcp_sa()
