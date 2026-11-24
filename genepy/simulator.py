import time
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
    def __init__(self, drawOnSkip: bool = False):
        self.drawOnSkip = drawOnSkip

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

        self._observers: list[Observer] = []

    def registerObserver(self, observer: Observer):
        self._observers.append(observer)

    def _tick(self):
        self.world.tick(self.timeUnit)
        
        for o in self._observers:
            o.onTick(self)

    def run(self):
        while True:
            for _ in range(self.framePerTick):
                self._tick()

            for o in self._observers:
                o.onFrame(self)

    def skip(self, second: float, LOG_INTERVAL: float = 10.0, FRAME_INTERVAL: float = 0.5):
        lastTick = 0
        skip = int(self.tickPerSec*second)

        start = lastLog = lastFrame = time.perf_counter()
        for i in range(skip):
            self.world.tick(self.timeUnit)
                    
            for o in self._observers:
                if not o.drawOnSkip: continue
                o.onTick(self)
    
            now = time.perf_counter()

            if now - lastFrame >= FRAME_INTERVAL:
                for o in self._observers:
                    if not o.drawOnSkip: continue
                    o.onFrame(self)
                    
                lastFrame = now

            if now - lastLog >= LOG_INTERVAL:
                done = i + 1
                speed = (done - lastTick) / (now - lastLog)                  # 최근 구간 tick/s
                eta = (skip - done) / speed if speed > 0 else float('inf')
    
                print(
                    f'[{now - start:7.1f}s] tick {done}/{skip} ({done / skip:6.2%}) '
                    f'| sim {done / self.tickPerSec / 60:6.1f}min | {speed:7.1f} tick/s | ETA {eta / 60:5.1f}min ',
                    flush=True,
                )
                lastLog, lastTick = now, done