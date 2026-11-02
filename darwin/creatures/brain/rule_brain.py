from typing import ClassVar

from .brain import Brain
from ..genome import BrainGene, UnitSpec, ProbUnit

class RuleBrain(Brain):
    def __init__(self, hostility):
        super().__init__()
        self.hostility = hostility

class RuleBrainGene(BrainGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('hostility', initValue=0.05, initStd=0.1, unitType=ProbUnit),
    )
    PRODUCT = RuleBrain