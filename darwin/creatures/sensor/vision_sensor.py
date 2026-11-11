import math
from typing import ClassVar, TYPE_CHECKING

from .sensor import Sensor, Stimulus

if TYPE_CHECKING:
    from ...object import Object
    from ..body import SelfState
    from ...tick_context import TickContext

class VisionSensor(Sensor):
    STIMULUS_NAME: ClassVar[str]
    TARGET: ClassVar[type]

    def __init__(self, fov: float, range: float):
        super().__init__()
        self.fov: float = fov
        self.range: float = range

    def _relativeAngle(self, dx: float, dy: float, rotation: float) -> float:
        return (math.degrees(math.atan2(dx, dy)) - rotation + 180) % 360 - 180

    def _dist(self, dx: float, dy: float) -> float:
        return math.sqrt(dx*dx+dy*dy)

    def sense(self, ctx: TickContext, state: SelfState) -> list[Stimulus]:
        stimuli: list[Stimulus] = []
        for obj in ctx.near(state.coord, self.range, kind=self.TARGET):
            dx, dy = ctx.displacement(state.coord, obj.coord)
            angle = self._relativeAngle(dx, dy, state.rotation)
            dist = self._dist(dx, dy)
            if 1e-6 < dist < self.range and abs(angle) < self.fov*180:
                stimuli.append(
                    Stimulus(
                        name=self.STIMULUS_NAME,
                        cause=self.TARGET,
                        intensity=self._intense(obj, dist, state),
                        direction=angle/180
                    )
                )
        return stimuli

    def _intense(self, obj: Object, dist: float, state: SelfState) -> float:
        """탐지 대상을 보고 자극의 크기를 결정합니다. 재정의 가능합니다."""
        return 1-dist/self.range