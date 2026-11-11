from .event import Event, Trigger
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..creatures import Creature
    from ..tick_context import TickContext

class AttackEvent(Event):
    def __init__(self, executor: Creature, target: Creature, attackEnergy: float, name: str = ''):
        super().__init__(f'AttackEvent({executor} -> {target})' if name == '' else name)
        self.executor = executor
        self.target = target
        self.attackEnergy = attackEnergy

    def notify(self):
        self.target.onEvent(AttackEvent, self.executor)

    def shoot(self, ctx: TickContext):
        self.target.spend(self.attackEnergy)

@dataclass(frozen=True)
class AttackTrigger(Trigger):
    target: Creature
    attackEnergy: float

    def by(self, executor: Creature) -> Event:
        return AttackEvent(executor, self.target, self.attackEnergy)