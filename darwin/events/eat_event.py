from .event import Event, Trigger
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..objects import Food
    from ..creatures import Creature
    from ..tick_context import TickContext

class EatEvent(Event):
    def __init__(self, executor: Creature, target: Food, name: str = ''):
        super().__init__(f'EatEvent({executor} -> {target})' if name == '' else name)
        self.executor = executor
        self.target = target

    def notify(self):
        self.target.onEvent(EatEvent, self.executor)

    def shoot(self, ctx: TickContext):
        if self.target in ctx.objects:
            ctx.objects.remove(self.target)
            self.executor.gain(self.target.spend(self.target.energy))

@dataclass(frozen=True)
class EatTrigger(Trigger):
    target: Food

    def by(self, executor: Creature) -> Event:
        return EatEvent(executor, self.target)