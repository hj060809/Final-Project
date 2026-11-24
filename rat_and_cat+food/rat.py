from genepy import *

from specious import CAT_SPECIOUS
import math
import numpy as np
import random

class CatVisionSensor(CreatureVisionSensor):
    STIMULUS_NAME: ClassVar[str] = "Cat"
    TARGET: ClassVar[type] = Creature

    def _filter(self, obj: Creature, _: SelfState):
        return obj.specious == CAT_SPECIOUS

class CatVisionSensorGene(CreatureVisionSensorGene):
    PRODUCT = CatVisionSensor
        
class RatBrain(Brain):
    CAUSES = (Food, Creature)
    TOP_K = 2

    def __init__(self, **weights: float):
        super().__init__()
        self.eat = 0
        self.W1 = np.array([weights[f'w1_{i}'] for i in range(N_HIDDEN * N_IN)]).reshape(N_HIDDEN, N_IN)
        self.W2 = np.array([weights[f'w2_{i}'] for i in range(N_OUT * N_HIDDEN)]).reshape(N_OUT, N_HIDDEN)

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

        intent: list[Trigger] = []
        if self.eat/observation.self.bodyState.maxEnergy > 1 and observation.self.energyRate > 0.8:
            self.eat -= observation.self.bodyState.maxEnergy*0.35
            intent.append(
                ReproduceTrigger('RAT')
            )

        return Judgement(
            turnSpeed=float(np.tanh(out[0])),
            speed=self._sigmoid(out[1]),
            intents = intent
        )

    def _relu(self, x):
        return np.maximum(0, x)

    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        if kind is not CollisionEvent:
            return Judgement()
        if isinstance(reqBy, Food):
            self.eat += reqBy.energy
            return Judgement(intents=[EatTrigger(reqBy)])
        return Judgement()
    
N_IN, N_HIDDEN, N_OUT = 14, 8, 2

class RatBrainGene(BrainGene):
    SCHEMA = (
        tuple(UnitSpec(f'w1_{i}', initValue=0.0, initStd=1 / math.sqrt(N_IN)) for i in range(N_HIDDEN * N_IN))
        + tuple(UnitSpec(f'w2_{i}', initValue=0.0, initStd=1 / math.sqrt(N_HIDDEN)) for i in range(N_OUT * N_HIDDEN))
    )
    PRODUCT = RatBrain


RAT_GENOME = Genome.init(
    bodyGene=TriangleBodyGene.init(
        units=(
            PositiveUnit.fromValue('maxEnergy', 200, 20, fixed=True),
            PositiveUnit.fromValue('whRatio', 2/math.sqrt(3), 0.1, fixed=True),
            PositiveUnit.fromValue('maxSpeed', 100, 2, fixed=True),
        )
    ),
    brainGene=RatBrainGene.init(),
    sensorGenes=[
        FoodVisionSensorGene.init(
            units=(
                ProbUnit.fromValue('fov', 0.8, 0.01, fixed=True),
                PositiveUnit.fromValue('range', 60, 4, fixed=True),
            )
        ),
        CatVisionSensor.init(
            units=(
                ProbUnit.fromValue('fov', 0.8, 0.01, fixed=True),
                PositiveUnit.fromValue('range', 60, 4, fixed=True),
            )
        )
    ],
    sensorGenePool=[
        FoodVisionSensorGene,
        CatVisionSensorGene
    ],
    fixedSensorTypes=True
)