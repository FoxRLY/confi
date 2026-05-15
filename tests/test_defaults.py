from typing import Literal
from dataclasses import dataclass, field
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
        "TEST_CLASS_FIELD_A": None,
    })

    @dataclass
    class TestClass:
        field_a: int = 10

    parsed_value = parse(TestClass)

    assert parsed_value.field_a == 10

def test_optional_types():
    set_environment({
        "TEST_CLASS_FIELD_A": None,
        "TEST_CLASS_FIELD_B": "32"
    })

    @dataclass
    class TestClass:
        field_a: int | None = None
        field_b: int | None = None

    parsed_value = parse(TestClass)

    assert parsed_value.field_a is None
    assert parsed_value.field_b == 32

def test_default_factory():
    set_environment({
        "TEST_CLASS_FIELD_A": None,
    })

    @dataclass
    class TestClass:
        field_a: int | None = field(default_factory=lambda: 10 + 32)

    parsed_value = parse(TestClass)

    assert parsed_value.field_a is 42

def test_literal():
    set_environment({
        "TEST_CLASS_FIELD_A": None,
    })

    @dataclass
    class TestClass:
        field_a: Literal["read", "write"] = "read"

    parsed_value = parse(TestClass)

    assert parsed_value.field_a == "read"

