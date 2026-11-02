import pygame
import math
from typing import TYPE_CHECKING, Callable, ClassVar
from .object import Object
from .creatures.creature import Creature
from .objects.food import Food
import ctypes
import sys

if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

if TYPE_CHECKING:
    from .world_state import WorldState

BG_COLOR = (24, 27, 34)
MAP_COLOR = (32, 36, 45)
GRID_COLOR = (42, 47, 58)
GRID_STEP = 10
SUPERSAMPLE = 2

class Viewer:
    _renderers: ClassVar[dict[type, Callable]] = {}

    @classmethod
    def renderer(cls, objType: type):
        def register(fn):
            cls._renderers[objType] = fn
            return fn
        return register

    def __init__(self, window: tuple[int, int] = (800, 600)):
        pygame.init()
        self.screen = pygame.display.set_mode(window)
        pygame.display.set_caption("Darwin Basic Viewer")
        self.canvas = pygame.Surface((window[0] * SUPERSAMPLE, window[1] * SUPERSAMPLE))
        self._scale = 1.0
        self._offset = (0.0, 0.0)
        self._worldHeight = 0

    def _fitTo(self, state: WorldState):
        """맵 비율을 유지한 채 화면 중앙에 맞춤"""
        w, h = self.canvas.get_size()
        self._scale = min(w / state.width, h / state.height)
        self._offset = (
            (w - state.width * self._scale) / 2,
            (h - state.height * self._scale) / 2,
        )
        self._worldHeight = state.height

    def toScreen(self, coord: tuple[float, float]) -> tuple[int, int]:
        """월드 좌표(y 위쪽이 +) → 픽셀 좌표(y 아래쪽이 +)"""
        return (
            round(self._offset[0] + coord[0] * self._scale),
            round(self._offset[1] + (self._worldHeight - coord[1]) * self._scale),
        )

    def _drawBackground(self, state: WorldState):
        self.canvas.fill(BG_COLOR)
        left, top = self.toScreen((0, state.height))
        right, bottom = self.toScreen((state.width, 0))
        pygame.draw.rect(self.canvas, MAP_COLOR, (left, top, right - left, bottom - top))

        for x in range(0, state.width + 1, GRID_STEP):
            pygame.draw.line(self.canvas, GRID_COLOR, self.toScreen((x, 0)), self.toScreen((x, state.height)), SUPERSAMPLE)
        for y in range(0, state.height + 1, GRID_STEP):
            pygame.draw.line(self.canvas, GRID_COLOR, self.toScreen((0, y)), self.toScreen((state.width, y)), SUPERSAMPLE)


    def toScreenLength(self, length: float) -> int:
        """월드 길이 → 픽셀 길이 (최소 1픽셀)"""
        return max(1, round(length * self._scale))

    def _draw(self, obj: Object):
        for kind in type(obj).__mro__:
            if kind in self._renderers:
                self._renderers[kind](self, obj)
                return
        raise TypeError(f'no renderer for {type(obj).__name__}')

    def render(self, state: WorldState):
        self._fitTo(state)
        self._drawBackground(state)
        for obj in sorted(state.objects, key=lambda o: isinstance(o, Creature)):    # Creature를 위에 그림
            self._draw(obj)
        pygame.transform.smoothscale(self.canvas, self.screen.get_size(), self.screen)
        pygame.display.flip()

    def run(self, simulator):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            simulator.tick()
            self.render(simulator.state)
            clock.tick(simulator.fps)  # Limit to 60 FPS

        self.close()

    def close(self):
        pygame.quit()

def _polygonOf(viewer: Viewer, collider) -> list[tuple[int, int]]:
    return [
        viewer.toScreen((collider.centerX + x, collider.centerY + y))
        for x, y in collider.vertFromCenter
    ]

def lighten(color: tuple[int, int, int], t: float = 0.55) -> tuple[int, int, int]:
    return tuple(round(c + (255 - c) * t) for c in color)

@Viewer.renderer(Object)
def drawObject(viewer: Viewer, obj: Object):
    points = _polygonOf(viewer, obj.collider)
    pygame.draw.polygon(viewer.canvas, obj.color, points)
    pygame.draw.polygon(viewer.canvas, lighten(obj.color), points, SUPERSAMPLE)

@Viewer.renderer(Food)
def drawFood(viewer: Viewer, food: Food):
    pygame.draw.circle(viewer.canvas, food.color, viewer.toScreen(food.coord), viewer.toScreenLength(food.size))
    pygame.draw.circle(viewer.canvas, lighten(food.color), viewer.toScreen(food.coord), viewer.toScreenLength(food.size), SUPERSAMPLE)

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