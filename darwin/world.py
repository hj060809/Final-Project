import math
import statistics
from .events import CollisionEvent
from .tick_context import TickContext
from typing import TYPE_CHECKING, Iterator, Callable

if TYPE_CHECKING:
    from .events import Event
    from .object import Object, Collider

"""
전체 world
- 데이터와 함수를 모두 보유
"""
class EventScheduler:
    def __init__(
            self, 
            action: Callable[[TickContext], list[Event]],
            tickCondition: Callable[[int], bool] = lambda _: True, 
            objCondition: Callable[[list[Object]], bool] = lambda _: True, 
        ):
        self.tickCondition = tickCondition
        self.objCondition = objCondition
        self.action = action

    def onTick(self, ctx: TickContext, ticks: int) -> list[Event]:
        if self.tickCondition(ticks) and self.objCondition(ctx.objects):
            return self.action(ctx)
        return []

class SpatialGrid:
    def __init__(self, objects: list[Object], width: int, height: int):
        self.width = width
        self.height = height
        self._objects = objects

        self.colliders = {o: o.collider for o in objects} # collider는 한 번 계산하여 box 생성
        self.boxes = [ # 콜라이더를 감싸는 박스, 중심과 반높이/반너비
            (self.colliders[o].centerX, self.colliders[o].centerY, *self.colliders[o].extents())
            for o in objects # obj 속 인덱스 유지
        ]

        # 분할할 칸 사이즈와 칸 개수 계산
        extents = [max(b[2], b[3]) for b in self.boxes]
        cellSize = max(4 * statistics.median(extents), 1e-9) if extents else max(width, height)
        
        self.cols, self.rows = max(1, int(width // cellSize)), max(1, int(height // cellSize))
        self.cellW, self.cellH = width / self.cols, height / self.rows

        self.cell2boxes: dict[int, list[int]] = {} # cell 인덱스 -> 걸친 box 인덱스 리스트
        for i, (x, y, halfW, halfH) in enumerate(self.boxes):
            for key in self._cover(x, y, halfW, halfH):
                self.cell2boxes.setdefault(key, []).append(i)

    def _cover(self, x: float, y: float, hw: float, hh: float) -> list[int]:
        """주어진 박스가 걸친 cell의 인덱스를 반환"""
        x0, x1 = math.floor((x - hw) / self.cellW), math.floor((x + hw) / self.cellW)
        y0, y1 = math.floor((y - hh) / self.cellH), math.floor((y + hh) / self.cellH)
        xs = range(self.cols) if x1 - x0 + 1 >= self.cols else [v % self.cols for v in range(x0, x1 + 1)]
        ys = range(self.rows) if y1 - y0 + 1 >= self.rows else [v % self.rows for v in range(y0, y1 + 1)]
        return [cx + cy * self.cols for cx in xs for cy in ys]

    def near(self, coord: tuple[float, float], radius: float, kind: type[Object]) -> Iterator[Object]:
        seen: set[int] = set()
        for key in self._cover(coord[0], coord[1], radius, radius): # coord 중심으로 radius 만큼의 box를 가정 -> cell 인덱스 조회
            for i in self.cell2boxes.get(key, []): # 해당 cell에 걸친 box 조회
                if i not in seen:
                    seen.add(i)
                    if isinstance(self._objects[i], kind):
                        yield self._objects[i] # 본 적 없고, type이면 반환

    def overlapsInCell(self) -> list[tuple[Object, Object]]:
        """같은 셀 위에 있는 오브젝트를 반환"""
        W, H = self.width, self.height
        halfW, halfH = W / 2, H / 2
        n = len(self._objects)
        seen: set[int] = set()
        result: list[tuple[Object, Object]] = []

        for members in self.cell2boxes.values(): # 모든 격자 cell을 순회
            for i, objIdx1 in enumerate(members): # 한 cell에 있는 멤버 순회
                ax, ay, ahw, ahh = self.boxes[objIdx1] # 짝을 찾을 box
                for objIdx2 in members[i + 1:]: # 나머지 멤버 순회
                    bx, by, bhw, bhh = self.boxes[objIdx2] # 짝을 찾을 box

                    # cell 내에서 box가 겹치는가? -> 대략적인 충돌 검사
                    if abs((bx - ax + halfW) % W - halfW) > ahw + bhw:
                        continue
                    if abs((by - ay + halfH) % H - halfH) > ahh + bhh:
                        continue

                    key = objIdx1 * n + objIdx2 # 두 오브젝트 쌍에 대한 고유 key 생성
                    if key not in seen:
                        seen.add(key)
                        result.append((self._objects[objIdx1], self._objects[objIdx2]))

        return result
class World:
    def __init__(self, width: int, height: int, initObjects: list[Object], eventSchedulers: list[EventScheduler] = []):
        self.width = width
        self.height = height
        self._objects = initObjects
        self.eventSchedulers = eventSchedulers
        self.ticks = 0

    def tick(self, timeUnit: float):
        objSearchHelper = SpatialGrid(self._objects, self.width, self.height)
        ctx = TickContext(
            self.width,
            self.height,
            self._objects,
            timeUnit,
            objSearchHelper
        )

        for a, b, mtv in self._detectCollision(objSearchHelper): # 충돌 해소
            CollisionEvent(a, b, mtv).call(ctx)

        requested: list[Event] = []

        for es in self.eventSchedulers:
            requested.extend(es.onTick(ctx, self.ticks))

        for o in self._objects: # sensor 처리 등 obj 개별 행동 완료
            requested.extend(o.onTick(ctx))

        for e in requested:
            e.call(ctx)

        for obj in self._objects:
            obj.coord = self._wrap(obj.coord)

        self.ticks += 1

    def _wrap(self, coord: tuple[float, float]) -> tuple[float, float]:
        x, y = coord
        return (x % self.width, y % self.height)

    def _detectCollision(self, broadPhaseHelper: SpatialGrid) -> list[tuple[Object, Object, tuple[float, float]]]:
        if len(self._objects) < 2:
            return []

        expected = broadPhaseHelper.overlapsInCell()
        colliders = broadPhaseHelper.colliders

        collisionPairs: list[tuple[Object, Object]] = []
        for a, b in expected:
            if not (a.COLLISION_DETECTION or b.COLLISION_DETECTION):
                continue
            mtv = self._computeMTV(colliders[a], colliders[b])
            if not mtv is None:
                collisionPairs.append((a, b, mtv))

        return collisionPairs

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