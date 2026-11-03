from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .object import Object

@dataclass
class TickContext:
    _objects: list[Object]
    _timeUnit: float

    @property
    def objects(self) -> list[Object]:
        return self._objects

    @property
    def timeUnit(self) -> float:
        return self._timeUnit

    @objects.setter
    def objects(self, _: list[Object]):
        raise AttributeError("Only read, append, remove access is allowed for 'objects' property.")