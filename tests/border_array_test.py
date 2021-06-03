from pystr.border_array import border_array, strict_border_array


def test_empty() -> None:
    assert border_array("") == []
    assert strict_border_array("") == []


def test_aaba() -> None:
    assert border_array("aaba") == [0, 1, 0, 1]
    assert strict_border_array("aaba") == [0, 1, 0, 1]


def test_aaa() -> None:
    assert border_array("aaa") == [0, 1, 2]
    assert strict_border_array("aaa") == [0, 0, 2]


def test_aaaba() -> None:
    assert border_array("aaaba") == [0, 1, 2, 0, 1]
    assert strict_border_array("aaaba") == [0, 0, 2, 0, 1]


def test_aaabaaabaaabaaa() -> None:
    assert border_array("aaabaaabaaabaaa") == \
        [0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert strict_border_array("aaabaaabaaabaaa") == \
        [0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 11]
    #    a  a  a  b  a  a  a  b  a  a  a  b  a  a  a


def check_border(x: str, ba: list[int]) -> None:
    for i, b in enumerate(ba):
        assert b <= i
        assert x[:b] == x[i-b+1:i+1]


def check_strict(x: str, ba: list[int]) -> None:
    for i, b in enumerate(ba):
        assert b == 0 or i == len(x) - 1 or x[b] != x[i+1]

# FIXME: Check if a border is the longest...


def test_border() -> None:
    for x in [
        "aaa", "aaba",
        "aaaba", "aaabaaabaaabaaa",
        "aaabaaacaaabaaa"
    ]:
        check_border(x, border_array(x))
        check_border(x, strict_border_array(x))
        check_strict(x, strict_border_array(x))
