from dataclasses import dataclass
from os import environ
from typing import Annotated, Literal
from confi import parse
from pprint import pprint


def set_environment(variables: dict[str, str | None]):
    for name, value in variables.items():
        if value is None:
            environ.pop(name, None)
        else:
            environ[name] = value

set_environment({
    "EXAMPLE_A": "1",
    "EXAMPLE_BETTER_A": "ONE",
    "EXAMPLE_C": "1",
    "EXAMPLE_D": "read",
    "EXAMPLE_INNER_A": "1",
    "EXAMPLE_F": "1",
    "EXAMPLE_G": None,
    "EXAMPLE_H": None,
    "EXAMPLE_I": None,
})

@dataclass
class ExampleInner:
    a: int

@dataclass
class Example:
    a: int
    better_a: int | str
    c: str | int
    d: Literal["read", "write"]
    e: ExampleInner
    f: Annotated[int, lambda x: x + 10]
    g: int = 10
    h: int | None = None
    i: Literal["read", "write"] = "write"

example = parse(Example)

pprint(example)
