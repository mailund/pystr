import _setup  # noqa: F401

from pystr.exact import border, kmp, naive
from pystr.cols import bright_white, bright_green


INTERACTIVE = False  # Must be false in test suite...


def run_iter(i):
    for _ in i:
        pass


def test_border_kmp():
    x = "aaaxaaab"
    p = "aaab"
    print(bright_white("NAIVE"))
    run_iter(naive(x, p, progress=True, interactive=INTERACTIVE))
    print(bright_white("KMP"))
    run_iter(kmp(x, p, progress=True, interactive=INTERACTIVE))
    print(bright_white("BORDER"))
    run_iter(border(x, p, progress=True, interactive=INTERACTIVE))


from pystr.border_array import *

if __name__ == '__main__':
    INTERACTIVE = True  # Run interactive if we use as a script
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(bright_green(name))
            f()
