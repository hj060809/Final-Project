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
class IsoscelesTriangleCollider(Collider):
    width: float = 0
    height: float = 0

    def localPoints(self):
        hw = self.width / 2
        return ((0, self.height), (hw, 0), (-hw, 0))

@dataclass
class RegularPolygonCollider(Collider):
    radius: float
    n: int
    
    def localPoints(self):
        angle = math.radians(360/self.n)
        return ((self.radius*math.sin(i*angle), self.radius*math.cos(i*angle)) for i in range(self.n))

class Object:
    COLLISION_DETECTION: ClassVar[bool] = False # Collision 연산에 고려할지
    IS_FIXED: ClassVar[bool] = True # 충돌 시 현 위치를 고정할지
    IS_SOLID: ClassVar[bool] = True # 충돌 시 상대가 날 뚫고 지나갈지

    def __init__(
            self,
            name: str,
            initCoord: tuple[float, float],
            initRotation: float,
            initEnergy: float,
            color: tuple[int, int, int] = (0, 0, 0)
        ):
        self.coord = initCoord
        self._rotation = initRotation
        self._maxEnergy = initEnergy
        self._energy = initEnergy*1
        self.name = name
        self.color = color
        self.eventQueue = []

        self.totalGain = 0 # <임시 요소 입니다. 제거 요망>

    def __repr__(self):
        return f'Object({self.name}, {self.coord})'

    @property
    def energy(self) -> float:
        return self._energy

    def spend(self, amount: float) -> float:
        paid = min(amount, self.energy)
        self._energy -= paid
        return paid

    def gain(self, amount: float):
        self.totalGain += amount # <임시 요소 입니다. 제거 요망>
        self._energy = min(self._maxEnergy, self._energy+amount)

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, newRot: float) -> float:
        self._rotation = newRot%360

    @property
    def collider(self) -> Collider:
        raise NotImplementedError("collider property must be implemented in subclasses.")

    def enqueueEvent(self, e: Event):
        self.eventQueue.append(e)

    def move(self, dx: float, dy: float):
        self.coord = (self.coord[0]+dx, self.coord[1]+dy)

    def act(self, ctx: TickContext) -> list[Event]:
        raise NotImplementedError("onTick() method must be implemented in subclasses.")
    
    def onTick(self, ctx: TickContext):
        self.act(ctx)
        requested = self.eventQueue.copy()
        self.eventQueue = []
        return requested
    
    def onCollision(self, other: Object, mtv: tuple[float, float]):
        if self.IS_FIXED or not other.IS_SOLID:
            return

        if other.IS_FIXED:
            self.move(mtv[0], mtv[1])
        else:
            self.move(mtv[0]/2, mtv[1]/2)

    def onEvent(self, kind: type[Event], reqBy: Object):
        raise NotImplementedError("onEvent() method must be implemented in subclasses.")