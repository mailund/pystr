import random
from pystr_vis.cols import green, red, blue
from pystr_vis.colour_segments import colour


def test_colour_segments():
    n = 25
    m = 10
    x = 'a' * n
    for _ in range(15):
        c = colour(x)
        print(c)
        for _ in range(m):
            j = random.randrange(1, n)
            i = random.randrange(j)
            c[i:j, random.choice([green, red, blue])]
        print(c)  # triggers the segment processing

        # negative segments
        c = colour(x)
        print(c)
        for _ in range(m):
            j = random.randrange(1, n)
            i = random.randrange(j)
            c[-j:-i, random.choice([green, red, blue])]
        print(c)  # triggers the segment processing


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            print(name)
            f()
