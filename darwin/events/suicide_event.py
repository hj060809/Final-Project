from .event import Event, Trigger
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..object import Object
    from ..tick_context import TickContext

class SuicideEvent(Event):
    def __init__(self, executor: Object, name: str = ''):
        super().__init__(f'SuicideEvent({executor})' if name == '' else name)
        self.executor = executor

    def notify(self):
        self.executor.onEvent(SuicideEvent, self.executor)

    def shoot(self, ctx: TickContext):
        if self.executor in ctx.objects:
            ctx.objects.remove(self.executor)

@dataclass(frozen=True)
class SuicideTrigger(Trigger):
    def by(self, executor: Object) -> Event:
        return SuicideEvent(executor)