from typing import ClassVar

from ..genome import SensorGene, UnitSpec, ProbUnit, PositiveUnit
from ...objects import Food
from .vision_sensor import VisionSensor

class FoodVisionSensor(VisionSensor):
    STIMULUS_NAME: ClassVar[str] = "Appetite"
    TARGET: ClassVar[type] = Food

class FoodVisionSensorGene(SensorGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('fov', initValue=0.2, initStd=0.1, unitType=ProbUnit), # 좌우 반각
        UnitSpec('range', initValue=15, initStd=3, unitType=PositiveUnit)
    )
    PRODUCT = FoodVisionSensor