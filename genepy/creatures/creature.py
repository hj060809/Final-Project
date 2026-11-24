from dataclasses import dataclass, field
from ..object import Object
from ..objects import Food
from ..events import SuicideEvent, GenEvent
from .constraints import ActionFlow
from .specious import Specious
from typing import TYPE_CHECKING, ClassVar, Callable
import numpy as np

if TYPE_CHECKING:
    from .genome import Genome
    from ..tick_context import TickContext
    from .body import SelfState
    from .sensor import Stimulus
    from .brain import Judgement
    from ..events import Event
    from .body import BodyState

@dataclass
class SelfState:
    coord: tuple[float, float]
    rotation: float
    energy: float
    specious: Specious
    genome: Genome
    bodyState: BodyState

    @property
    def energyRate(self) -> float:
        return self.energy/self.bodyState.maxEnergy

@dataclass
class Observation:
    self: SelfState
    stimuli: list[Stimulus] = field(default_factory=list)

    def of(self, cause: type, condition: Callable[[Stimulus], bool] = lambda s: True) -> list[Stimulus]:
        return [s for s in self.stimuli if issubclass(s.cause, cause) if condition(s)]

    def strongest(self, cause: type, condition: Callable[[Stimulus], bool] = lambda s: True) -> Stimulus | None:
        return max(self.of(cause, condition=condition), key=lambda s: s.intensity, default=None)

class Creature(Object):
    COLLISION_DETECTION: ClassVar[bool] = True
    IS_FIXED: ClassVar[bool] = False
    
    def __init__(
            self,
            name: str,
            initCoord: tuple[float, float],
            initRotation: float,
            genome: Genome,
            specious: Specious,
            color: tuple[float, float, float],
        ):
        self.genome = genome
        
        phenoType = self.genome.express()

        self.body = phenoType.body
        self.brain = phenoType.brain
        self.sensors = phenoType.sensors

        self.specious = specious
        self._age = 0

        super().__init__(name, initCoord, initRotation, self.body.maxEnergy, color=color)

    def turn(self, dTheta: float):
        self.rotation += dTheta

    def forward(self, d: float):
        dy = d*np.cos((self.rotation%360)*np.pi/180)
        dx = d*np.sin((self.rotation%360)*np.pi/180)
        self.move(dx, dy)

    @property
    def collider(self):
        return self.body.getCollider(self.rotation, self.coord)

    @property
    def state(self) -> SelfState:
        return SelfState(
            coord=self.coord,
            rotation=self.rotation,
            energy=self.energy,
            specious=self.specious,
            genome=self.genome,
            bodyState=self.body.state
        )

    @property
    def age(self) -> int:
        return self._age

    def act(self, ctx: TickContext):
        self._age += 1
        state = self.state
        obs = Observation(self=state)

        for sensor in self.sensors:
            obs.stimuli.extend(sensor.sense(ctx, state))

        self._carryOut(self.brain.think(obs), ctx.timeUnit, ctx)

    def onEvent(self, kind: type[Event], reqBy: Object):
        self._carryOut(self.brain.react(kind, reqBy, state = self.state), timeUnit=0, ctx=None)

    def _carryOut(self, judgement: Judgement, timeUnit: float, ctx: TickContext | None):
        dist, turn = self.body.toMovement(judgement.speed, judgement.turnSpeed, timeUnit)

        actionFlow = ActionFlow(
            timeUnit=timeUnit,
            dist=dist,
            turn=turn,
            intents=judgement.intents,
            ctx=ctx
        )
        cost = sum([c.cost(self, actionFlow) for c in self.specious.constraints])

        self.spend(cost)
        if self.energy <= 0:
            self.enqueueEvent(SuicideEvent(self))
            self.enqueueEvent(
                GenEvent(
                    targetType=Food,
                    name=self.name,
                    energy=self.energy,
                    radius=(self.body.size**0.5)/2,
                    initCoord=self.coord,
                    initRotation=0,
                    expirationTime=60,
                )
            )
            return

        self.turn(turn)
        self.forward(dist)
        for action in judgement.intents:
            self.enqueueEvent(action.by(self))

