from ..object import Object
from ..objects import Obstacle, Food
from ..events import KillEvent, GenEvent
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar
import numpy as np
import random

if TYPE_CHECKING:
    from ..events import Event
    from .genome import Genome
    from ..world_state import WorldState

"""
어떻게 감각하고 행동할 것인가?
    - 통일된 자료구조가 필요하다!

1. Sense, Action?
    - 모든 센서가 하나의 Sense 형태로 값을 담아 반환?
    - brain이 모든 Sense를 읽고 Action 리스트를 반환
    - Creature에서 Event를 생성

2. Observation, Judgement 인터페이스
    - 한 Observation를 생성
    - 모든 센서의 관찰을 Obs에 기록
    - Brain은 Obs에서 원하는 데이터만 읽어 판단
    - Judgement 반환
    - Creature가 다시 Event와 Action으로 변환
    - 실행

    * 먹기는 Event가 아니라 닿으면 자동으로 섭취 (Size 안쪽이면 섭취)
    * 공격은 Event?
    * 번식은...


* 주변 인구밀도가 지속적으로 높으면 자살 메커니즘 필요
"""

class Creature(Object):
    COLLISION_DETECTION: ClassVar[bool] = True
    COLOR: tuple[int, int, int] = (0, 0, 255)
    
    def __init__(
            self,
            name: str,
            initCoord: tuple[float, float],
            initRotation: float,
            genome: Genome,
            color: tuple[float, float, float]
        ):
        super().__init__(name, initCoord, initRotation, color=color)
        self.genome = genome
        
        phenoType = self.genome.express()

        self.body = phenoType.body
        self.brain = phenoType.brain
        self.sensors = phenoType.sensors

    def polarMove(self, d: float, theta: float = 0):
        dy = d*np.cos(((self.rotation+theta)%360)*np.pi/180)
        dx = d*np.sin(((self.rotation+theta)%360)*np.pi/180)
        self.move(dx, dy)

    def move(self, dx: float, dy: float):
        self.coord = (self.coord[0]+dx, self.coord[1]+dy)

    def turn(self, dTheta: float):
        self.rotation += dTheta

    @property
    def collider(self):
        return self.body.getCollider(self.rotation, self.coord)

    def act(self, state: WorldState, timeUnit: float) -> list[Event]:
        """
        body의 업데이트 + 상태 보고 (Time flow)
        sensor의 감지 (Sense)
        brain의 판단 (Think)
        body 적용 (Act)
        Event 반환 (Change)
        """
        for sensor in self.sensors:
            sensor.sense(state, (*self.coord, self.rotation))

        self.polarMove(self.body.maxSpeed*timeUnit)
        if random.random() > 0.99:
            self.turn((2*random.random()-1)*120)
        self.body.health -= timeUnit
        if self.body.health < 0:
            return [
                KillEvent(self, self),
                GenEvent(
                    Creature,
                    name=self.name,
                    initCoord=self.coord,
                    initRotation=self.rotation,
                    genome=self.genome.mutate(),
                    color=self.color
                )
            ]
        return []

    def onCollision(self, other: Object, mtv: tuple[float, float]):
        if isinstance(other, Food):
            pass
        elif isinstance(other, Obstacle):
            self.move(mtv[0], mtv[1])
        elif isinstance(other, Creature):
            self.move(mtv[0]/2, mtv[1]/2)