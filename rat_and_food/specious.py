from genepy import Specious
from genepy.creatures.constraints import *

RAT_SPECIOUS = Specious(
    name='RAT',
    constraints=[
        UpkeepConstraint(multiplier=0.2),
        TurnConstraint(multiplier=0.1),
        MovementConstraint(multiplier=0.005),
        AttackConstraint(),
        ReproduceConstraint()
    ]
)