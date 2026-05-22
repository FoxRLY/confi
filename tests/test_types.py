from typing import Literal
import pytest
from dataclasses import dataclass
from os import environ
from confi import parse

def set_environment(variables: dict[str, str | None]):
    for name, value in variables.items():
        if value is None:
            environ.pop(name, None)
        else:
            environ[name] = value

def test_builtin_types():
    set_environment({
        "TEST_CLASS_FIELD_A": "125",
        "TEST_CLASS_FIELD_B": "12.34",
        "TEST_CLASS_FIELD_C": "Hello",
        "TEST_CLASS_FIELD_D": "true",
    })

    @dataclass
    class TestClass:
        field_a: int
        field_b: float
        field_c: str
        field_d: bool

    parsed_value = parse(TestClass)

    assert parsed_value.field_a == 125
    assert parsed_value.field_b == 12.34
    assert parsed_value.field_c == "Hello"
    assert parsed_value.field_d == True

def test_builtin_type_failing():
    set_environment({
        "TEST_CLASS_FIELD_A": "Hello",
    })

    @dataclass
    class TestClass:
        field_a: int

    with pytest.raises(ValueError):
        parse(TestClass)

def test_union_type():
    set_environment({
        "TEST_CLASS_FIELD_A": "Hello",
    })

    @dataclass
    class TestClass:
        field_a: int | str

    parsed_value = parse(TestClass)

    assert type(parsed_value.field_a) is str
    assert parsed_value.field_a == "Hello"

def test_union_type_order_precedence():
    set_environment({
        "TEST_CLASS_FIELD_A": "20",
    })

    @dataclass
    class TestClass:
        field_a: str | int

    parsed_value = parse(TestClass)

    assert type(parsed_value.field_a) is str
    assert parsed_value.field_a == "20"

def test_literal():
    set_environment({
        "TEST_CLASS_FIELD_A": "read",
    })

    @dataclass
    class TestClass:
        field_a: Literal["read", "write"]

    parsed_value = parse(TestClass)

    assert type(parsed_value.field_a) is str
    assert parsed_value.field_a == "read"

def test_literal_failing():
    set_environment({
        "TEST_CLASS_FIELD_A": "other",
    })

    @dataclass
    class TestClass:
        field_a: Literal["read", "write"]

    with pytest.raises(ValueError):
        parse(TestClass)

