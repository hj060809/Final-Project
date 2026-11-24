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

    def _intense(self, obj: Object, dist: float, state: SelfState) -> float:
        """탐지 대상을 보고 자극의 크기를 결정합니다. 재정의 가능합니다."""
        return 1-dist/self.range

class CatVisionSensorGene(CreatureVisionSensorGene):
    PRODUCT = CatVisionSensor

N_IN, N_HIDDEN, N_OUT = 7, 8, 2
class RatNet:
    def __init__(self, weights: dict[str, float]):
        self.W1 = np.array([weights[f'w1_{i}'] for i in range(N_HIDDEN * N_IN)]).reshape(N_HIDDEN, N_IN)
        self.W2 = np.array([weights[f'w2_{i}'] for i in range(N_OUT * N_HIDDEN)]).reshape(N_OUT, N_HIDDEN)

    def _sigmoid(self, v: float, range: float = 50) -> float:
        return 1 / (1 + math.exp(-max(-range, min(range, v))))

    def forward(self, x) -> tuple[float, float]:
        hidden = np.tanh(self.W1 @ x)
        out = self.W2 @ hidden

        turn = float(np.tanh(out[0]))
        speed = self._sigmoid(out[1])

        return turn, speed
 
class RatBrain(Brain):
    CAUSES = (Creature,)
    TOP_K = 2

    def __init__(self, **weights: dict[str, float]):
        super().__init__()
        self.net = RatNet(weights=weights)

    def encode(self, obs: Observation) -> np.ndarray:
        x = []
        for cause in self.CAUSES:
            stimuli = sorted(obs.of(cause), key=lambda s: s.intensity, reverse=True)[:self.TOP_K]
            for i in range(self.TOP_K):
                if i < len(stimuli):
                    s = stimuli[i]
                    a = s.direction * math.pi
                    x += [s.intensity, math.sin(a), math.cos(a)]
                else:
                    x += [0.0, 0.0, 0.0]          # 감지한 것이 없으면 0
        x += [1.0]           # 자기 상태, 상수(편향)
        return np.array(x)

    def think(self, observation: Observation) -> Judgement:
        x = self.encode(observation)
        turn, speed = self.net.forward(x)

        return Judgement(
            turnSpeed=turn,
            speed=speed,
        )
    
    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        return Judgement()

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
            PositiveUnit.fromValue('maxSpeed', 150, 2),
            ProbUnit.fromValue('maxTurnRate', 0.9, 0.1, fixed=True),
        )
    ),
    brainGene=RatBrainGene.init(),
    sensorGenes=[
        CatVisionSensorGene.init(
            units=(
                ProbUnit.fromValue('fov', 0.995, 0.01, fixed=True),
                PositiveUnit.fromValue('range', 80, 4, fixed=True),
            )
        )
    ],
    sensorGenePool=[
        CatVisionSensorGene
    ],
    fixedSensorTypes=True
)