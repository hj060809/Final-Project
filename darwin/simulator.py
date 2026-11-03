from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World

"""
최상위 클래스
- world를 보유하고 tick() 호출
- 한 틱의 결과를 return
- viewer는 simulator 결과를 모르고 반환값으로만 draw
"""

class Observer:
    def onTick(self, simulator: Simulator):
        raise NotImplementedError("onTick() must be implemented in subclass.")

    def onFrame(self, simulator: Simulator):
        raise NotImplementedError("onFrame() must be implemented in subclass.")

class Simulator:
    def __init__(
            self,
            world: World,
            tickPerSec: int = 60,
            framePerTick: int = 1
        ):
        self.world = world
        self.tickPerSec = tickPerSec
        self.framePerTick = framePerTick

        self.timeUnit = 1/self.tickPerSec
        self.ticks = 0

        self._observers: list[Observer] = []

    def registerObserver(self, observer: Observer):
        self._observers.append(observer)

    def _tick(self):
        self.world.tick(self.timeUnit)
        self.ticks += 1
        
        for o in self._observers:
            o.onTick(self)

    def run(self):
        while True:
            for _ in range(self.framePerTick):
                self._tick()

            for o in self._observers:
                o.onFrame(self)