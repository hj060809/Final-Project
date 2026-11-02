from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world_state import WorldState

class Event:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name
    
    def shoot(self, state: WorldState):
        raise NotImplementedError("shoot() method must be implemented in subclasses.")