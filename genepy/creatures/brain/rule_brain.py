from typing import ClassVar, TYPE_CHECKING
import math
import random

from .brain import Brain, Judgement
from ..genome import BrainGene, UnitSpec, ProbUnit
from ...events import CollisionEvent, EatTrigger, AttackTrigger, ReproduceTrigger
from ...objects import Food
from ..creature import Creature

if TYPE_CHECKING:
    from ..creature import Observation
    from ...events import Event
    from ...object import Object
    from ..creature import SelfState
    from ..sensor import Stimulus

class RuleBrain(Brain):
    def __init__(self, hostility: float, cowardice: float, power: float):
        super().__init__()
        self.hostility = hostility
        self.cowardice = cowardice
        self.power = power

    @staticmethod
    def _meanDir(sts: list[Stimulus]) -> float:
        """자극 방향의 intensity 가중 평균. 방향은 -1~1(= -180~180도), 빈 리스트면 0"""
        x = sum(s.intensity * math.cos(s.direction * math.pi) for s in sts)
        y = sum(s.intensity * math.sin(s.direction * math.pi) for s in sts)
        if x == 0 and y == 0:
            return 0.0
        return math.atan2(y, x) / math.pi

    @staticmethod
    def _reverseDir(dir: float) -> float:
        """반대 방향. 0(정면) → -1(뒤), 0.5(오른쪽) → -0.5(왼쪽)"""
        return (dir + 2) % 2 - 1

    def think(self, observation: Observation) -> Judgement:
        nearestFood = observation.strongest(Food)
        threat = observation.of(Creature, condition=lambda s: s.intensity > 1-self.cowardice)
        prey = observation.of(Creature, condition=lambda s: s.intensity < self.hostility)

        if threat:
            runaway = self._reverseDir(self._meanDir(threat))
            return Judgement(
                turnSpeed=runaway,
                speed=1
            )

        if nearestFood and observation.self.energyRate < 0.95:
            return Judgement(
                turnSpeed=nearestFood.direction,
                speed=1
            )
        elif prey and observation.self.energyRate < 0.90:
            return Judgement(
                turnSpeed=self._meanDir(prey),
                speed=1
            )
        else:
            return Judgement(
                turnSpeed=(random.random()-0.5 if random.random() > 0.99 else 0),
                speed=0.5
            )

    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        if kind is CollisionEvent and isinstance(reqBy, Food):
            return Judgement(intents=[EatTrigger(reqBy)])
        if kind is CollisionEvent and isinstance(reqBy, Creature):
            return Judgement(intents=[AttackTrigger(reqBy, min(reqBy.energy, state.energy*self.power))])
        
        return Judgement()

class RuleBrainGene(BrainGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('hostility', initValue=0.5, initStd=0.1, unitType=ProbUnit),
        UnitSpec('cowardice', initValue=0.5, initStd=0.1, unitType=ProbUnit),
        UnitSpec('power', initValue=0.2, initStd=0.05, unitType=ProbUnit),
    )
    PRODUCT = RuleBrain