from typing import ClassVar, TYPE_CHECKING
import math

from .body import Body
from ..genome import BodyGene, UnitSpec, PositiveUnit, ProbUnit
from ...object import IsoscelesTriangleCollider

class TriangleBody(Body):
    def __init__(
            self,
            maxEnergy: float,
            whRatio: float,
            maxTurnRate: float,
            maxSpeed: float
        ):
        super().__init__(maxEnergy, maxTurnRate, maxSpeed)
        self.whRatio = whRatio
        self.width = math.sqrt(2*self.size*whRatio)
        self.height = math.sqrt(2*self.size/whRatio)

    def getCollider(self, direction: float, coord: tuple[float, float]) -> IsoscelesTriangleCollider:
        return IsoscelesTriangleCollider(
            direction=direction,
            centerX=coord[0],
            centerY=coord[1],
            width=self.width,
            height=self.height
        )

class TriangleBodyGene(BodyGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('maxEnergy', initValue=300, initStd=50, unitType=PositiveUnit),
        UnitSpec('whRatio', initValue=2/math.sqrt(3), initStd=0.1, unitType=PositiveUnit),
        UnitSpec('maxSpeed', initValue=8, initStd=10, unitType=PositiveUnit),
        UnitSpec('maxTurnRate', initValue=2/3, initStd=0.1, unitType=ProbUnit)
    )
    PRODUCT: ClassVar[type] = TriangleBody