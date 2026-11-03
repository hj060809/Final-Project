from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...tick_context import TickContext

class Sensor:
    def __init__(self):
        pass

    def sense(self, ctx: TickContext, heading: tuple[float, float, float]):
        raise NotImplementedError('sense() method must be implemented in subclasses.')