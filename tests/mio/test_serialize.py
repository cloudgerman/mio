from datetime import datetime

from mio._serialize import serialize


def test_int() -> None:
    assert serialize(1) == 1


def test_str() -> None:
    assert serialize("a") == "a"


def test_float() -> None:
    assert serialize(1.2) == 1.2


def test_datetime() -> None:
    d = datetime.now()
    assert serialize(d) == d.isoformat()


def test_list() -> None:
    i_values = [1, 2]
    assert serialize(i_values) == i_values

    s_values = ["a", ""]
    assert serialize(s_values) == ["a"]


def test_set() -> None:
    values = {1, 2}
    assert serialize(values) == list(sorted(values))


def test_dict() -> None:
    values = {"a": 1, "b": 2}
    assert serialize(values) == values

    values = {"permissions": 1}
    assert not serialize(values)

    values = {"abc": 0}
    assert not serialize(values)


def test_obj() -> None:
    class X:
        c = 1
        permissions = ["a"]
        skip: list[int] = []

    x = X()
    assert serialize(x) == {"c": 1}
