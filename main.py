
from dataclasses import dataclass, field
from os import environ
from typing import Annotated, Literal

from confi import parse

environ["BRUH_KWUH_A"] = "10"
environ["BRUH_KWUH_B"] = "2.32"
environ["BRUH_KWUH_C"] = "223"
environ["BRUH_KWUH_D"] = "Vlad"
environ["BRUH_KWUH_INNER_A"] = "meow"



@dataclass(frozen=True)
class BruhKwuhInner:
    a: Literal["read", "write", "bruh"]

@dataclass(frozen=True)
class BruhKwuh:
    a: int
    b: Annotated[float | int , lambda x: x + 2.32]
    inner: BruhKwuhInner
    c: int | None = field(default_factory=lambda: 10)
    d: Annotated[str | None, lambda x: x + ", Hello!"] = None

a = parse(BruhKwuh)
print(a)

