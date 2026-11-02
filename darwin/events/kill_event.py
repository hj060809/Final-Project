from .event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..object import Object
    from ..world_state import WorldState

class KillEvent(Event):
    def __init__(self, executor: Object, target: Object, name: str = ''):
        super().__init__(f'KillEvent({executor} -> {target})' if name == '' else name)
        self.target = target

    def shoot(self, state: WorldState):
        state.objects.remove(self.target)