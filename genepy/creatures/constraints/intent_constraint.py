from .constraint import Constraint
from ...events import AttackTrigger, ReproduceTrigger 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..creature import Creature
    from .constraint import ActionFlow
    from ...events import Trigger

class IntentConstraint(Constraint):
    def _getIntent(self, actionflow: ActionFlow, intentType: type[Trigger]) -> list[Trigger]:
        return [i for i in actionflow.intents if isinstance(i, intentType)]
    
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        raise NotImplementedError('cost() must be implemented in subclasses.')

class AttackConstraint(IntentConstraint):
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        intents: list[AttackTrigger] = self._getIntent(actionflow, AttackTrigger)
        return sum(i.attackEnergy for i in intents)*self._multiplier

class ReproduceConstraint(IntentConstraint):
    def cost(self, creature: Creature, actionflow: ActionFlow) -> float:
        count = len(self._getIntent(actionflow, ReproduceTrigger))
        return count*creature.body.maxEnergy*0.2