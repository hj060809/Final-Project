from typing import ClassVar, TYPE_CHECKING

from .body import Body
from ..genome import BodyGene, UnitSpec, PositiveUnit
from ...object import RectCollider

class RectBody(Body):
    def __init__(
            self,
            health: float,
            width: float,
            height: float,
            maxSpeed: float,
        ):
        super().__init__(health, maxSpeed)
        self.width = width
        self.height = height

    def getCollider(self, direction: float, coord: tuple[float, float]) -> RectCollider:
        return RectCollider(
            direction=direction,
            centerX=coord[0],
            centerY=coord[1],
            width=self.width,
            height=self.height
        )

class RectBodyGene(BodyGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('health', initValue=100, initStd=10, unitType=PositiveUnit),
        UnitSpec('width', initValue=20, initStd=4, unitType=PositiveUnit),
        UnitSpec('height', initValue=20, initStd=4, unitType=PositiveUnit),
        UnitSpec('maxSpeed', initValue=30, initStd=10, unitType=PositiveUnit)
    )
    PRODUCT: ClassVar[type] = RectBody