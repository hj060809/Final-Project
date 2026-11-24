from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..creature import Observation
    from ...events import Event, Trigger
    from ...object import Object
    from ..creature import SelfState


@dataclass
class Judgement:
    turnSpeed: float = 0
    speed: float = 0
    intents: list[Trigger] = field(default_factory=list)

    def __post_init__(self):
        if not -1 <= self.turnSpeed <= 1:
            raise ValueError('turnSpeed must be between -1 ~ 1')
        if not 0 <= self.speed <= 1:
            raise ValueError('speed must be between 0 ~ 1')
        
class Brain:
    def think(self, observation: Observation) -> Judgement:
        """매 틱마다 sensor 관측 결과를 토대로 판단"""
        raise NotImplementedError("think() method must be implemented in subclasses.")

    def react(self, kind: type[Event], reqBy: Object, state: SelfState) -> Judgement:
        """자신에게 이벤트 발생시 대응/기억"""
        raise NotImplementedError("react() method must be implemented in subclasses.")