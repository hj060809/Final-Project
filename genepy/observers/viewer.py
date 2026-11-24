import pygame
import math
from typing import TYPE_CHECKING, Callable, ClassVar

from ..creatures.sensor import FoodVisionSensor, CreatureVisionSensor
from ..object import Object
from ..creatures.creature import Creature
from ..objects.food import Food
from ..simulator import Observer
import ctypes
import sys

if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

if TYPE_CHECKING:
    from ..world import World
    from ..simulator import Simulator

BG_COLOR = (24, 27, 34)
MAP_COLOR = (32, 36, 45)
GRID_COLOR = (42, 47, 58)
GRID_STEP = 10
SUPERSAMPLE = 2

ARC_STEP = 6

class Viewer(Observer):
    _renderers: ClassVar[dict[type, Callable]] = {}
    _sensorRenderers: ClassVar[dict[type, Callable]] = {}

    @classmethod
    def sensorRenderer(cls, sensorType: type):
        def register(fn):
            cls._sensorRenderers[sensorType] = fn
            return fn
        return register

    @classmethod
    def renderer(cls, objType: type):
        def register(fn):
            cls._renderers[objType] = fn
            return fn
        return register

    def __init__(self, window: tuple[int, int] = (600, 600), drawOnSkip: bool = False,):
        super().__init__(drawOnSkip=drawOnSkip)
        
        pygame.init()
        self.screen = pygame.display.set_mode(window)
        pygame.display.set_caption("Darwin Basic Viewer")
        self.canvas = pygame.Surface((window[0] * SUPERSAMPLE, window[1] * SUPERSAMPLE))
        self._scale = 1.0
        self._offset = (0.0, 0.0)
        self._worldHeight = 0
        self.clock = pygame.time.Clock()
        self.overlay = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
        self.showSensors = True

    def _fitTo(self, mapWidth: int, mapHeight: int):
        """맵 비율을 유지한 채 화면 중앙에 맞춤"""
        w, h = self.canvas.get_size()
        self._scale = min(w / mapWidth, h / mapHeight)
        self._offset = (
            (w - mapWidth * self._scale) / 2,
            (h - mapHeight * self._scale) / 2,
        )
        self._worldHeight = mapHeight

    def toScreen(self, coord: tuple[float, float]) -> tuple[int, int]:
        """월드 좌표(y 위쪽이 +) → 픽셀 좌표(y 아래쪽이 +)"""
        return (
            round(self._offset[0] + coord[0] * self._scale),
            round(self._offset[1] + (self._worldHeight - coord[1]) * self._scale),
        )

    def _drawBackground(self, mapWidth: int, mapHeight: int):
        self.canvas.fill(BG_COLOR)
        left, top = self.toScreen((0, mapHeight))
        right, bottom = self.toScreen((mapWidth, 0))
        pygame.draw.rect(self.canvas, MAP_COLOR, (left, top, right - left, bottom - top))

        for x in range(0, mapWidth + 1, GRID_STEP):
            pygame.draw.line(self.canvas, GRID_COLOR, self.toScreen((x, 0)), self.toScreen((x, mapHeight)), SUPERSAMPLE)
        for y in range(0, mapHeight + 1, GRID_STEP):
            pygame.draw.line(self.canvas, GRID_COLOR, self.toScreen((0, y)), self.toScreen((mapWidth, y)), SUPERSAMPLE)
    
    def _drawSensors(self, creature: Creature):
        for sensor in creature.sensors:
            for kind in type(sensor).__mro__:
                if kind in self._sensorRenderers:
                    self._sensorRenderers[kind](self, creature, sensor)
                    break

    def toScreenLength(self, length: float) -> int:
        """월드 길이 → 픽셀 길이 (최소 1픽셀)"""
        return max(1, round(length * self._scale))

    def _draw(self, obj: Object):
        for kind in type(obj).__mro__:
            if kind in self._renderers:
                self._renderers[kind](self, obj)
                return
        raise TypeError(f'no renderer for {type(obj).__name__}')

    def render(self, world: World):
        self._fitTo(world.width, world.height)
        self._drawBackground(world.width, world.height)

        creatures = [o for o in world._objects if isinstance(o, Creature)]
        for obj in world._objects:
            if not isinstance(obj, Creature):
                self._draw(obj)

        if self.showSensors:                      # 먹이 위, Creature 아래
            self.overlay.fill((0, 0, 0, 0))
            for c in creatures:
                self._drawSensors(c)
            self.canvas.blit(self.overlay, (0, 0))

        for c in creatures:
            self._draw(c)

        pygame.transform.smoothscale(self.canvas, self.screen.get_size(), self.screen)
        pygame.display.flip()

    def onFrame(self, simulator: Simulator):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.showSensors = not self.showSensors     # S 키로 켜고 끄기

        self.render(simulator.world)
        self.clock.tick(simulator.tickPerSec)

    def onTick(self, simulator: Simulator):
        pass

    def close(self):
        pygame.quit()

def _polygonOf(viewer: Viewer, collider) -> list[tuple[int, int]]:
    return [
        viewer.toScreen((collider.centerX + x, collider.centerY + y))
        for x, y in collider.vertFromCenter
    ]

def lighten(color: tuple[int, int, int], t: float = 0.55) -> tuple[int, int, int]:
    return tuple(round(c + (255 - c) * t) for c in color)

def sectorPoints(viewer: Viewer, center, rotation: float, halfAngle: float, radius: float):
    """시선 방향 기준 ±halfAngle 범위의 부채꼴 꼭짓점. 180 이상이면 원"""
    if halfAngle >= 180:
        start, end, points = rotation - 180, rotation + 180, []
    else:
        start, end, points = rotation - halfAngle, rotation + halfAngle, [viewer.toScreen(center)]

    steps = max(2, math.ceil((end - start) / ARC_STEP))
    for k in range(steps + 1):
        t = math.radians(start + (end - start) * k / steps)
        points.append(viewer.toScreen((center[0] + radius * math.sin(t), center[1] + radius * math.cos(t))))
    return points

@Viewer.sensorRenderer(FoodVisionSensor)
def drawFoodVision(viewer: Viewer, creature: Creature, sensor: FoodVisionSensor):
    points = sectorPoints(viewer, creature.coord, creature.rotation, sensor.fov * 180, sensor.range)
    pygame.draw.polygon(viewer.overlay, (126, 217, 111, 28), points)                # 채우기
    pygame.draw.polygon(viewer.overlay, (126, 217, 111, 90), points, SUPERSAMPLE)   # 테두리

@Viewer.sensorRenderer(CreatureVisionSensor)
def drawCreatureVision(viewer: Viewer, creature: Creature, sensor: CreatureVisionSensor):
    points = sectorPoints(viewer, creature.coord, creature.rotation, sensor.fov * 180, sensor.range)
    pygame.draw.polygon(viewer.overlay, (217, 111, 126, 28), points)                # 채우기
    pygame.draw.polygon(viewer.overlay, (217, 111, 126, 90), points, SUPERSAMPLE)   # 테두리

@Viewer.renderer(Object)
def drawObject(viewer: Viewer, obj: Object):
    points = _polygonOf(viewer, obj.collider)
    pygame.draw.polygon(viewer.canvas, obj.color, points)
    pygame.draw.polygon(viewer.canvas, lighten(obj.color), points, SUPERSAMPLE)

@Viewer.renderer(Food)
def drawFood(viewer: Viewer, food: Food):
    pygame.draw.circle(viewer.canvas, food.color, viewer.toScreen(food.coord), viewer.toScreenLength(food.radius))
    pygame.draw.circle(viewer.canvas, lighten(food.color), viewer.toScreen(food.coord), viewer.toScreenLength(food.radius), SUPERSAMPLE)

@Viewer.renderer(Creature)
def drawCreature(viewer: Viewer, creature: Creature):
    drawObject(viewer, creature)

    collider = creature.collider
    t = math.radians(creature.rotation)
    fx, fy = math.sin(t), math.cos(t)       # 앞쪽
    rx, ry = fy, -fx                        # 오른쪽
    half = collider.height / 2
    wing = collider.width * 0.32
    cx, cy = collider.centerX, collider.centerY

    arrow = (
        (cx + fx * half * 1.55, cy + fy * half * 1.55),
        (cx + fx * half * 0.75 - rx * wing, cy + fy * half * 0.75 - ry * wing),
        (cx + fx * half * 0.75 + rx * wing, cy + fy * half * 0.75 + ry * wing),
    )
    pygame.draw.polygon(viewer.canvas, lighten(creature.color), [viewer.toScreen(p) for p in arrow])