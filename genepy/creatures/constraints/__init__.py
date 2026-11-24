from .constraint import Constraint, MultipleConstraint, ActionFlow

from .movement_constraint import MovementConstraint, TurnConstraint
from .upkeep_constraint import UpkeepConstraint
from .intent_constraint import IntentConstraint, AttackConstraint, ReproduceConstraint

CONSTRAINT_PACK = [
    MovementConstraint(),
    TurnConstraint(),
    UpkeepConstraint(),
    AttackConstraint(),
    ReproduceConstraint()
]