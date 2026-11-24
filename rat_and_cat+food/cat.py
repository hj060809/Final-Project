from genepy import *
import random
from specious import RAT_SPECIOUS

class RatVisionSensor(CreatureVisionSensor):
    STIMULUS_NAME: ClassVar[str] = "Rat"
    TARGET: ClassVar[type] = Creature

    def _filter(self, obj: Creature, _: SelfState):
        return obj.specious == RAT_SPECIOUS

class RatVisionSensorGene(CreatureVisionSensorGene):
    PRODUCT = RatVisionSensor

class CatBrain(Brain):
    def __init__(self, power: float):
        super().__init__()
        self.power = power

    def think(self, obs: Observation) -> Judgement:
        target = obs.strongest(Creature)
        if not target:
            return Judgement(
                turnSpeed = (2*random.random()-1) if random.random() > 0.99 else 0,
                speed=0.75
            )

        return Judgement(
            turnSpeed=target.direction,
            speed=1
        )

    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        if kind is CollisionEvent and isinstance(reqBy, Creature) and reqBy.specious == RAT_SPECIOUS:
            return Judgement(intents=[AttackTrigger(reqBy, reqBy.energy)])
        return Judgement()

class CatBrainGene(BrainGene):
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = (
        UnitSpec('power', initValue=0.2, initStd=0.05, unitType=ProbUnit),
    )
    PRODUCT = CatBrain

CAT_GENOME = Genome.init(
    bodyGene=RectBodyGene.init(
        units=(
            PositiveUnit.fromValue('maxEnergy', 1500, 20, fixed=True),
            PositiveUnit.fromValue('maxSpeed', 60, 2, fixed=True),
        )
    ),
    brainGene=CatBrainGene.init(
        units=(
            ProbUnit.fromValue('power', 0.1, 0.01, fixed=True),
        ),
    ),
    sensorGenes=[
        RatVisionSensorGene.init(
            units=(
                ProbUnit.fromValue('fov', 0.25, 0.01, fixed=True),
                PositiveUnit.fromValue('range', 40, 0.01, fixed=True),
            )
        )
    ],
    sensorGenePool=[RatVisionSensorGene]
)