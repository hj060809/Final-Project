from .constraint import Constraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..creature import Creature
    from .constraint import ActionFlow

class UpkeepConstraint(Constraint):
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        return actionflow.timeUnit*creature.body.size*self._multiplier