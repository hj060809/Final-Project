from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world_state import WorldState

class Sensor:
    def __init__(self):
        pass

    def sense(self, state: WorldState, heading: tuple[float, float, float]):
        raise NotImplementedError('sense() method must be implemented in subclasses.')