from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...object import Collider

class Body:
    def __init__(
            self,
            health: float,
            maxSpeed: float,
        ):
        self.health = health
        self.maxSpeed = maxSpeed

    def getCollider(self, direction: float, coord: tuple[float, float]) -> Collider:
        raise NotImplementedError("collider property must be implemented in subclasses.")
     
    def state(self):
        """자기 상태 보고...?"""
        pass