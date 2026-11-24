from genepy import Specious
from genepy.creatures.constraints import *

CAT_SPECIOUS = Specious(
    name='CAT',
    constraints=[]
)

RAT_SPECIOUS = Specious(
    name='RAT',
    constraints=[
        TurnConstraint(multiplier=0.001)
    ]
)