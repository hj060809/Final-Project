from typing import TYPE_CHECKING, Iterator
from dataclasses import dataclass

if TYPE_CHECKING:
    from .object import Object
    from .world import SpatialGrid

@dataclass
class TickContext:
    width: int
    height: int
    _objects: list[Object]
    _timeUnit: float
    _searchHelper: SpatialGrid

    def displacement(self, a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
        """a에서 b로 가는 최단 벡터"""
        dx = (b[0] - a[0] + self.width / 2) % self.width - self.width / 2
        dy = (b[1] - a[1] + self.height / 2) % self.height - self.height / 2
        return (dx, dy)
    
    def near(self, coord: tuple[float, float], radius: float, kind: type[Object]) -> Iterator[Object]:
        """coord 중심으로 radius 범위 내에 있는 kind type의 오브젝트를 반환"""
        return self._searchHelper.near(coord, radius, kind)
    
    @property
    def objects(self) -> list[Object]:
        return self._objects

    @property
    def timeUnit(self) -> float:
        return self._timeUnit

    @objects.setter
    def objects(self, _: list[Object]):
        raise AttributeError("Only read, append, remove access is allowed for 'objects' property.")