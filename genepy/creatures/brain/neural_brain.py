from typing import TYPE_CHECKING
import math
import numpy as np
from ..genome import BrainGene, UnitSpec
from ...events import CollisionEvent, EatTrigger, AttackTrigger
from .brain import Brain, Judgement
from ...objects import Food
from ..creature import Creature
import random

if TYPE_CHECKING:
    from ..creature import Observation
    from ...events import Event
    from ...object import Object
    from ..creature import SelfState
        
class NeuralBrain(Brain):
    CAUSES = (Food, Creature)
    TOP_K = 2

    def __init__(self, **weights: float):
        super().__init__()
        self.W1 = np.array([weights[f'w1_{i}'] for i in range(N_HIDDEN * N_IN)]).reshape(N_HIDDEN, N_IN)
        self.W2 = np.array([weights[f'w2_{i}'] for i in range(N_OUT * N_HIDDEN)]).reshape(N_OUT, N_HIDDEN)
        self._eatWill = 0.0
        self._attackWill = 0.0

    def _sigmoid(self, v: float, range: float = 50) -> float:
        return 1 / (1 + math.exp(-max(-range, min(range, v))))

    def encode(self, obs: Observation) -> np.ndarray:
        x = []
        for cause in self.CAUSES:
            stimuli = sorted(obs.of(cause), key=lambda s: s.intensity, reverse=True)[:self.TOP_K]
            for i in range(self.TOP_K):
                if i < len(stimuli):
                    s = stimuli[i]
                    a = s.direction * math.pi
                    x += [s.intensity, s.intensity * math.sin(a), s.intensity * math.cos(a)]
                else:
                    x += [0.0, 0.0, 0.0]          # 감지한 것이 없으면 0
        x += [obs.self.energyRate, 1.0]           # 자기 상태, 상수(편향)
        return np.array(x)

    def think(self, observation: Observation) -> Judgement:
        x = self.encode(observation)
        hidden = np.tanh(self.W1 @ x)
        out = self.W2 @ hidden

        self._eatWill = self._sigmoid(out[2])
        self._attackWill = self._sigmoid(out[3])

        return Judgement(
            turnSpeed=float(np.tanh(out[0])),
            speed=self._sigmoid(out[1]),
        )

    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        if kind is not CollisionEvent:
            return Judgement()
        if isinstance(reqBy, Food) and self._eatWill > random.random():
            return Judgement(intents=[EatTrigger(reqBy)])
        if isinstance(reqBy, Creature) and self._attackWill > random.random():
            return Judgement(intents=[AttackTrigger(reqBy, min(reqBy.energy, state.energy * 0.1))])
        return Judgement()
    
N_IN, N_HIDDEN, N_OUT = 14, 8, 4

class NeuralBrainGene(BrainGene):
    SCHEMA = (
        tuple(UnitSpec(f'w1_{i}', initValue=0.0, initStd=1 / math.sqrt(N_IN)) for i in range(N_HIDDEN * N_IN))
        + tuple(UnitSpec(f'w2_{i}', initValue=0.0, initStd=1 / math.sqrt(N_HIDDEN)) for i in range(N_OUT * N_HIDDEN))
    )
    PRODUCT = NeuralBrain
