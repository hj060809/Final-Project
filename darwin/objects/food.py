from functools import cached_property

from ..object import Object, RegularPolygonCollider
from ..events import Event, KillEvent, GenEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world_state import WorldState

class Food(Object):
    def __init__(
            self,
            name: str,
            energy: float,
            size: float,
            initCoord: tuple[float, float],
            initRotation: float = 0,
            expirationTime: float = 60 # tick
        ):
        super().__init__(name, initCoord, initRotation, color=(0,255,0))
        self.energy = energy
        self.size = size
        self._expirationTime = expirationTime

    @cached_property
    def collider(self):
        return RegularPolygonCollider(
            direction=self.rotation,
            centerX=self.coord[0],
            centerY=self.coord[1],
            radius=self.size,#width=self.size,
            n=6#height=self.size
        )

    def act(self, _: WorldState, timeUnit: float) -> list[Event]:
        self._expirationTime -= timeUnit
        if self._expirationTime < 0:
            return [
                KillEvent(self, self),
            ]

        return []

    def onCollision(self, other: Object, mtv: tuple[float, float]):
        self._expirationTime = 0
        self.energy = 0