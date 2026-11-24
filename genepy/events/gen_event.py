from .event import Event, Trigger
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..object import Object
    from ..tick_context import TickContext

class GenEvent(Event):
    def __init__(self, targetType: type[Object], **deps):
        super().__init__(f'GenEvent({targetType})')
        self.obj = targetType(**deps)

    def notify(self):
        pass

    def shoot(self, ctx: TickContext):
        ctx.objects.append(self.obj)

@dataclass(frozen=True)
class GenTrigger(Trigger):
    targetType: type[Object]
    deps: dict[str, Any]

    def by(self, executor: Object) -> Event:
        return GenEvent(executor, **self.deps)