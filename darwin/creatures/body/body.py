from dataclasses import dataclass
from typing import TYPE_CHECKING
from functools import cached_property

if TYPE_CHECKING:
    from ...object import Collider

@dataclass
class SelfState:
    coord: tuple[float, float]
    rotation: float
    energy: float
    energyRate: float
    maxSpeed: float
    size: float

class Body:
    def __init__(
            self,
            maxEnergy: float,
            maxSpeed: float
        ):
        self.maxEnergy = maxEnergy
        self.maxSpeed = maxSpeed

    @cached_property
    def size(self):
        raise NotImplementedError("size property must be implemented in subclasses.")

    def getCollider(self, direction: float, coord: tuple[float, float]) -> Collider:
        raise NotImplementedError("collider property must be implemented in subclasses.")
    
    def state(self, coord: tuple[float, float], rotation: float, energy: float) -> SelfState:
        return SelfState(
            coord=coord,
            rotation=rotation,
            energy=energy,
            energyRate=energy/self.maxEnergy,
            maxSpeed=self.maxSpeed,
            size = self.size
        )
    
    def toMovement(self, speedRate: float, turnRate: float, timeUnit: float) -> tuple[float, float]:
        return speedRate*self.maxSpeed*timeUnit, turnRate*180