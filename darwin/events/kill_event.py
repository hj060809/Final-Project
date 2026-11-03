from .event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..object import Object
    from ..tick_context import TickContext

class KillEvent(Event):
    def __init__(self, executor: Object, target: Object, name: str = ''):
        super().__init__(f'KillEvent({executor} -> {target})' if name == '' else name)
        self.target = target

    def shoot(self, ctx: TickContext):
        ctx.objects.remove(self.target)