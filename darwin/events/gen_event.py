from .event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world_state import WorldState
    from ..object import Object

class GenEvent(Event):
    def __init__(self, blueprint: type[Object], **info):
        super().__init__(f'GenEvent({blueprint.__name__}: {info})')
        self.obj = blueprint(**info)

    def shoot(self, state: WorldState):
        state.objects.append(self.obj)