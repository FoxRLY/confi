from typing import Annotated
from dataclasses import dataclass
from os import environ
from confi import parse

def set_environment(variables: dict[str, str | None]):
    for name, value in variables.items():
        if value is None:
            environ.pop(name, None)
        else:
            environ[name] = value

def test_simple_modificator():
    set_environment({
        "TEST_CLASS_FIELD_A": "9",
        "TEST_CLASS_FIELD_B": "13",
    })

    modificator = lambda x: x + 10 if x > 10 else 0

    @dataclass
    class TestClass:
        field_a: Annotated[int, modificator]
        field_b: Annotated[int, modificator]

    parsed_value = parse(TestClass)

    assert parsed_value.field_a == 0
    assert parsed_value.field_b == 23

def test_multiple_modificators():
    set_environment({
        "TEST_CLASS_FIELD_A": "a",
        "TEST_CLASS_FIELD_B": "b",
    })

    modificator_1 = lambda x: x + "+"
    modificator_2 = lambda x: x + "-"

    @dataclass
    class TestClass:
        field_a: Annotated[str, modificator_1, modificator_2]
        field_b: Annotated[str, modificator_2, modificator_1]

    parsed_value = parse(TestClass)

    assert parsed_value.field_a == "a+-"
    assert parsed_value.field_b == "b-+"

