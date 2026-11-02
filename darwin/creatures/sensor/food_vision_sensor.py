from typing import ClassVar, TYPE_CHECKING

from .sensor import Sensor
from ..genome import SensorGene, UnitSpec, ProbUnit, PositiveUnit

if TYPE_CHECKING:
    from ...world_state import WorldState

class FoodVisionSensor(Sensor):
    def __init__(self, fov, range):
        super().__init__()
        self.fov = fov
        self.range = range

    def sense(self, state: WorldState, heading: tuple[float, float, float]):
        pass

class FoodVisionSensorGene(SensorGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('fov', initValue=0.2, initStd=0.1, unitType=ProbUnit),
        UnitSpec('range', initValue=10, initStd=1, unitType=PositiveUnit)
    )
    PRODUCT = FoodVisionSensor