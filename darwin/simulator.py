from .world_state import WorldState
from .events import CollisionEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .events import Event

"""
run(), tick()을 통해 전체 시뮬레이션을 진행하는 최상위 클래스
"""

class Simulator:
    def __init__(self, state: WorldState, fps: int = 60):
        self.state = state
        self.fps = fps

    def tick(self):
        requested: Event = [CollisionEvent(a, b, mtv) for a, b, mtv in self.state.detectCollision()]
        
        for obj in self.state.objects:
            requested += obj.act(self.state, 1/self.fps)
            obj.coord = self.state.wrap(obj.coord)

        for e in requested:
            e.shoot(self.state)
        # 임시로 모든 Event 그냥 실행 (추후 우선순위/예외 로직 필요)