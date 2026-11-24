from dataclasses import dataclass
from typing import TYPE_CHECKING
from functools import cached_property

if TYPE_CHECKING:
    from ...object import Collider

@dataclass
class BodyState:
    maxEnergy: float
    maxSpeed: float
    maxTurnAngle: float
    size: float

class Body:
    def __init__(
            self,
            maxEnergy: float,
            maxTurnRate: float,
            maxSpeed: float
        ):
        if not -1 <= maxTurnRate <= 1:
            raise ValueError("maxTurnRate must be between -1~1")
        self.maxEnergy = maxEnergy
        self.maxTurnAngle = maxTurnRate*180
        self.maxSpeed = maxSpeed

    @cached_property
    def size(self) -> float:
        return self.maxEnergy/10

    def getCollider(self, direction: float, coord: tuple[float, float]) -> Collider:
        raise NotImplementedError("collider property must be implemented in subclasses.")

    @cached_property
    def state(self) -> BodyState:
        return BodyState(
            maxEnergy=self.maxEnergy,
            maxSpeed=self.maxSpeed,
            maxTurnAngle=self.maxTurnAngle,
            size = self.size
        )
    
    def toMovement(self, speedRate: float, turnRate: float, timeUnit: float) -> tuple[float, float]:
        return speedRate*self.maxSpeed*timeUnit, turnRate*self.maxTurnAngle*timeUnit