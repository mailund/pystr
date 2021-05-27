from pystr.exact import border, kmp
from pystr.cols import bright_white, bright_green


def run_iter(i):
    for _ in i:
        pass


def test_border_kmp():
    x = "aaaxaaab"
    p = "aaab"
    print(bright_white("BORDER"))
    run_iter(border(x, p, progress=True))
    #print(bright_white("KMP"))
    #run_iter(kmp(x, p, progress=True))


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(bright_green(name))
            f()
