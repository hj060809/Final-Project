from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..object import Object
    from ..tick_context import TickContext

class Event:
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name

    def call(self, ctx: TickContext):
        self.notify()
        self.shoot(ctx)

    def notify(self):
        raise NotImplementedError("notify() method must be implemented in subclasses.")
    
    def shoot(self, ctx: TickContext):
        raise NotImplementedError("shoot() method must be implemented in subclasses.")

@dataclass(frozen=True)
class Trigger:
    """Event 생성을 지연합니다."""
    def by(self, executor: Object) -> Event:
        raise NotImplementedError("by() method must be implemented in subclasses.")
