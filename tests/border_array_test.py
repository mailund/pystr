from pystr.border_array import border_array, strict_border_array


def test_empty():
    assert border_array("") == []
    assert strict_border_array("") == []


def test_selected():
    assert border_array("aaba") == [0, 1, 0, 1]
    assert strict_border_array("aaba") == [0, 1, 0, 1]

    assert border_array("aaa") == [0, 1, 2]
    assert strict_border_array("aaa") == [0, 0, 2]

    assert border_array("aaaba") == [0, 1, 2, 0, 1]
    assert strict_border_array("aaaba") == [0, 0, 2, 0, 1]
