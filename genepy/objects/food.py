from functools import cached_property

from ..object import Object, RegularPolygonCollider
from ..events import SuicideEvent
from .obstacle import Obstacle
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ..tick_context import TickContext
    from ..events import Event

class Food(Object):
    IS_SOLID: ClassVar[bool] = False

    def __init__(
            self,
            name: str,
            energy: float,
            radius: float,
            initCoord: tuple[float, float],
            initRotation: float = 0,
            expirationTime: float = 60 # sec
        ):
        super().__init__(name, initCoord, initRotation, energy, color=(0,255,0))
        self.radius = radius
        self._expirationTime = expirationTime

    @cached_property
    def collider(self):
        return RegularPolygonCollider(
            direction=self.rotation,
            centerX=self.coord[0],
            centerY=self.coord[1],
            radius=self.radius,
            n=6
        )

    def act(self, ctx: TickContext):
        self._expirationTime -= ctx.timeUnit
        if self._expirationTime < 0:
            self.enqueueEvent(SuicideEvent(self))

    def onEvent(self, kind: type[Event], reqBy: Object):
        pass