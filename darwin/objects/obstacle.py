from functools import cached_property

from ..object import Object, RectCollider
from ..events import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tick_context import TickContext

class Obstacle(Object):
    def __init__(
            self,
            name: str,
            width: float,
            height: float,
            initCoord: tuple[float, float],
            initRotation: float = 0
        ):
        super().__init__(name, initCoord, initRotation)
        self.width = width
        self.height = height

    @cached_property
    def collider(self):
        return RectCollider(
            direction=self.rotation,
            centerX=self.coord[0],
            centerY=self.coord[1],
            width=self.width,
            height=self.height
        )

    def act(self, ctx: TickContext) -> list[Event]:
        return []

    def onCollision(self, other: Object, mtv: tuple[float, float]):
        pass