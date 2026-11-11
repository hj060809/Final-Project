from typing import ClassVar, TYPE_CHECKING
import math

from .body import Body
from ..genome import BodyGene, UnitSpec, PositiveUnit
from ...object import RectCollider
from functools import cached_property

if TYPE_CHECKING:
    from ..brain import Judgement
    from ...events import Trigger

class RectBody(Body):
    def __init__(
            self,
            maxEnergy: float,
            whRatio: float,
            maxSpeed: float
        ):
        super().__init__(maxEnergy, maxSpeed)
        self.whRatio=whRatio
        self.width = math.sqrt(self.size*whRatio)
        self.height = math.sqrt(self.size/whRatio)
        
    @property
    def size(self):
        return self.maxEnergy/10

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
        UnitSpec('maxEnergy', initValue=300, initStd=50, unitType=PositiveUnit),
        UnitSpec('whRatio', initValue=1, initStd=0.1, unitType=PositiveUnit),
        UnitSpec('maxSpeed', initValue=8, initStd=10, unitType=PositiveUnit)
    )
    PRODUCT: ClassVar[type] = RectBody