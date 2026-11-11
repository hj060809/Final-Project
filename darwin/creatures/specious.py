from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .constraints import Constraint

@dataclass(frozen=True)
class Specious:
    name: str
    constraints: list[Constraint]

    def __eq__(self, value):
        return isinstance(value, Specious) and value.name == self.name