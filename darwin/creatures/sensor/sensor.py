from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..body import SelfState
    from ...tick_context import TickContext

@dataclass
class Stimulus:
    """direction은 왼쪽: (-), 오른쪽: (+)"""
    name: str
    cause: type
    intensity: float
    direction: float = 0.0

    def __post_init__(self):
        if not 0 <= self.intensity <= 1:
            raise ValueError('intensity must be between 0 ~ 1')
        if not -1 <= self.direction <= 1:
            raise ValueError('direction must be between -1 ~ 1')

class Sensor:
    def __init__(self):
        pass

    def sense(self, ctx: TickContext, state: SelfState) -> list[Stimulus]:
        raise NotImplementedError('sense() method must be implemented in subclasses.')