from functools import cached_property
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass
import math

if TYPE_CHECKING:
    from .events import Event
    from .tick_context import TickContext

"""
먹이, 개체를 포괄하는 추상 클래스
기본 기능을 포함한다
"""

@dataclass
class Collider:
    direction: float
    centerX: float
    centerY: float

    def localPoints(self) -> tuple[tuple[float, ...]]:
        """회전이 없을 때 중심 기준 꼭짓점 위치"""
        raise NotImplementedError("localPoints() method must be implemented in subclasses.")

    @cached_property
    def vertFromCenter(self) -> tuple[tuple[float, ...]]:
        """회전이 적용된 중심 기준 꼭짓점 위치"""
        t = math.radians(self.direction)
        sin, cos = math.sin(t), math.cos(t)
        return tuple((u * cos + v * sin, -u * sin + v * cos) for u, v in self.localPoints())

    @cached_property
    def normals(self) -> tuple[tuple[float, ...]]:
        """각 변의 normal vector 집합"""
        verts = self.vertFromCenter
        seen = []
        for i, (x0, y0) in enumerate(verts):
            x1, y1 = verts[(i + 1) % len(verts)]
            nx, ny = y0 - y1, x1 - x0
            length = math.hypot(nx, ny)
            if length == 0:
                continue
            nx, ny = nx / length, ny / length
            if not any(abs(nx * oy - ny * ox) < 1e-12 for ox, oy in seen):
                seen.append((nx, ny))      # 평행한 축은 한 번만 검사
        return tuple(seen)

    def projectTo(self, nx, ny) -> tuple[float, float]:
        """normal vector에 다각형 투영"""
        values = [x * nx + y * ny for x, y in self.vertFromCenter]
        return min(values), max(values)

    def extents(self):
        """중심 기준 경계 상자의 반폭, 반높이"""
        return max(abs(x) for x, _ in self.vertFromCenter), max(abs(y) for _, y in self.vertFromCenter)

@dataclass
class RectCollider(Collider):
    width: float = 0
    height: float = 0

    def localPoints(self):
        hw, hh = self.width / 2, self.height / 2
        return ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))

@dataclass
class RegularPolygonCollider(Collider):
    radius: float
    n: int
    
    def localPoints(self):
        angle = math.radians(360/self.n)
        return ((self.radius*math.sin(i*angle), self.radius*math.cos(i*angle)) for i in range(self.n))

class Object:
    COLLISION_DETECTION: ClassVar[bool] = False

    def __init__(
            self,
            name: str,
            initCoord: tuple[float, float],
            initRotation = float,
            color: tuple[int, int, int] = (0, 0, 0)
        ):
        self.coord = initCoord
        self._rotation = initRotation
        self.name = name
        self.color = color

    def __repr__(self):
        return f'Object({self.name}, {self.coord})'

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, newRot: float) -> float:
        self._rotation = newRot%360

    @property
    def collider(self) -> Collider:
        raise NotImplementedError("collider property must be implemented in subclasses.")

    def act(self, ctx: TickContext) -> list[Event]:
        raise NotImplementedError("tick() method must be implemented in subclasses.")

    def onCollision(self, other: Object, mtv: tuple[float, float]):
        raise NotImplementedError("onCollision() method must be implemented in subclasses.")