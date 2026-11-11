from typing import ClassVar, TYPE_CHECKING
import math

from ..genome import SensorGene, UnitSpec, ProbUnit, PositiveUnit
from ..creature import Creature
from .vision_sensor import VisionSensor

if TYPE_CHECKING:
    from ..body import SelfState

class CreatureVisionSensor(VisionSensor):
    STIMULUS_NAME: ClassVar[str] = "Creature"
    TARGET: ClassVar[type] = Creature

    def _intense(self, obj: Creature, dist: float, state: SelfState) -> float:
        """Creature를 감지합니다. 상대 사이즈에 따라 자극이 증폭됩니다."""
        return max(min(obj.body.size/state.size-0.5, 1), 0)

class CreatureVisionSensorGene(SensorGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('fov', initValue=0.75, initStd=0.05, unitType=ProbUnit), # 좌우 반각
        UnitSpec('range', initValue=20, initStd=3, unitType=PositiveUnit)
    )
    PRODUCT = CreatureVisionSensor