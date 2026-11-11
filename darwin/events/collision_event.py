from .event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..object import Object
    from ..tick_context import TickContext

class CollisionEvent(Event):
    def __init__(self, a: Object, b: Object, mtv: tuple[float, float], name: str = ''):
        super().__init__(f'CollisionEvent({a}, {b})' if name == '' else name)
        self.a = a
        self.b = b
        self.mtv = mtv

    def notify(self):
        self.a.onEvent(CollisionEvent, self.b)
        self.b.onEvent(CollisionEvent, self.a)
        
    def shoot(self, _: TickContext):
        self.a.onCollision(self.b, (-self.mtv[0], -self.mtv[1]))
        self.b.onCollision(self.a, self.mtv)