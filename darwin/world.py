import math
import statistics
from .events import CollisionEvent
from .tick_context import TickContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .events import Event
    from .object import Object, Collider

"""
전체 world
- 데이터와 함수를 모두 보유
"""

class World:
    def __init__(self, width: int, height: int, initObjects: list[Object]):
        self.width = width
        self.height = height
        self._objects = initObjects

    def tick(self, timeUnit: float):
        ctx = TickContext(self._objects, timeUnit)
        requested: list[Event] = [CollisionEvent(a, b, mtv) for a, b, mtv in self._detectCollision()]

        for o in self._objects:
            requested.extend(o.act(ctx))

        for e in requested:
            e.shoot(ctx)

        for obj in self._objects:
            obj.coord = self._wrap(obj.coord)

    def _wrap(self, coord: tuple[float, float]) -> tuple[float, float]:
        x, y = coord
        return (x % self.width, y % self.height)

    def _detectCollision(self) -> list[tuple[Object, Object, tuple[float, float]]]:
        _objects = self._objects

        n = len(_objects)
        if n < 2:
            return []

        colliders = {o: o.collider for o in _objects}

        expected = self._broadDetect(_objects, colliders)

        collides: list[tuple[Object, Object]] = []
        for a, b in expected:
            if not (a.COLLISION_DETECTION or b.COLLISION_DETECTION):
                continue
            mtv = self._computeMTV(colliders[a], colliders[b])
            if not mtv is None:
                collides.append((a, b, mtv))

        return collides

    def _broadDetect(self, _objects: list[Object], colliders: dict[Object, Collider]) -> list[tuple[Object, Object]]:
        W, H = self.width, self.height
        boxes = [
            (colliders[o].centerX, colliders[o].centerY, *colliders[o].extents())
            for o in _objects
        ]

        # 칸 크기는 중앙값 기준. 큰 객체는 걸치는 칸마다 넣음
        cell = max(4 * statistics.median(max(b[2], b[3]) for b in boxes), 1e-9)
        cols, rows = max(1, int(W // cell)), max(1, int(H // cell))
        cellW, cellH = W / cols, H / rows

        cells: dict[int, list[int]] = {}
        for i, (x, y, ex, ey) in enumerate(boxes):
            x0, x1 = math.floor((x - ex) / cellW), math.floor((x + ex) / cellW)
            y0, y1 = math.floor((y - ey) / cellH), math.floor((y + ey) / cellH)
            xs = range(cols) if x1 - x0 + 1 >= cols else [v % cols for v in range(x0, x1 + 1)]
            ys = range(rows) if y1 - y0 + 1 >= rows else [v % rows for v in range(y0, y1 + 1)]
            for cx in xs:
                for cy in ys:
                    cells.setdefault(cx + cy * cols, []).append(i)

        n = len(_objects)
        halfW, halfH = W / 2, H / 2
        seen: set[int] = set()
        pairs: list[tuple[Object, Object]] = []

        for members in cells.values():
            for p, i in enumerate(members):
                ax, ay, aex, aey = boxes[i]
                for j in members[p + 1:]:
                    bx, by, bex, bey = boxes[j]
                    if abs((bx - ax + halfW) % W - halfW) > aex + bex:
                        continue
                    if abs((by - ay + halfH) % H - halfH) > aey + bey:
                        continue
                    key = i * n + j
                    if key in seen:
                        continue
                    seen.add(key)
                    pairs.append((_objects[i], _objects[j]))

        return pairs

    def _computeMTV(self, a: Collider, b: Collider) -> tuple[float, float] | None:
        """충돌하면 b를 밀어낼 벡터를, 충돌하지 않으면 None을 반환합니다."""
        dx, dy = self._displacement((a.centerX, a.centerY), (b.centerX, b.centerY))

        best = math.inf
        mx = my = 0.0

        for axes in (a.normals, b.normals):
            for ax, ay in axes:
                aMin, aMax = a.projectTo(ax, ay)
                bMin, bMax = b.projectTo(ax, ay)
                offset = dx * ax + dy * ay

                pushPlus = aMax - (bMin + offset)
                pushMinus = (bMax + offset) - aMin

                if pushPlus < 0 or pushMinus < 0:
                    return None     # 분리축 발견

                if pushPlus < best:
                    best, mx, my = pushPlus, ax * pushPlus, ay * pushPlus
                if pushMinus < best:
                    best, mx, my = pushMinus, -ax * pushMinus, -ay * pushMinus

        return mx, my

    def _displacement(self, a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
        """a에서 b로 가는 최단 벡터"""
        dx = (b[0] - a[0] + self.width / 2) % self.width - self.width / 2
        dy = (b[1] - a[1] + self.height / 2) % self.height - self.height / 2
        return (dx, dy)