from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ...events.event import Trigger
    from ..creature import Creature
    from ...tick_context import TickContext


@dataclass(frozen=True)
class ActionFlow:
    """한 번의 _carryOut에서 일어난 일과 그때의 상황"""
    timeUnit: float
    dist: float
    turn: float
    intents: list[Trigger]
    ctx: TickContext | None

class Constraint:
    def __init__(self, multiplier: float = 1):
        self._multiplier = multiplier

    """Creature의 행동에 energy 비용을 부과하여 환경 적응을 유도합니다"""
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        """한 timeUnit에서 적용될 cost"""
        raise NotImplementedError('cost() must be implemented in subclasses.')

class MultipleConstraint(Constraint):
    def __init__(self, cons: list[Constraint], combineLogic: Callable[[list[float]], float] = sum):
        self.cons = cons
        self.combineLogic = combineLogic

    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        return self.combineLogic([c.cost(creature, actionflow) for c in self.cons])