from .constraint import Constraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..creature import Creature
    from .constraint import ActionFlow

class MovementConstraint(Constraint):
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        return actionflow.dist*creature.body.size*self._multiplier

class TurnConstraint(Constraint):
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        return abs(actionflow.turn)*creature.body.size*self._multiplier/180