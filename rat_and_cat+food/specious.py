from genepy import Specious
from genepy.creatures.constraints import *

CAT_SPECIOUS = Specious(
    name='CAT',
    constraints=[]
)

RAT_SPECIOUS = Specious(
    name='RAT',
    constraints=[
        UpkeepConstraint(multiplier=0.006),
        TurnConstraint(multiplier=0.01),
        MovementConstraint(multiplier=0.005),
        AttackConstraint(),
        ReproduceConstraint()
    ]
)