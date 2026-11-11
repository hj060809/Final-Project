from .event import Event, Trigger
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..tick_context import TickContext
    from ..creatures import Creature

def _mixTuple(t1: tuple[float, ...], t2: tuple[float, ...]) -> tuple[float, ...]:
    return tuple((e1+e2)/2 for e1, e2 in zip(t1, t2))

class ReproduceEvent(Event):
    def __init__(self, parent: Creature, partner: Creature| None, childName: str, temp: float = 0.2):
        super().__init__(f'ReproduceEvent({parent}, {partner})')
        if partner is None:
            partner = parent

        if parent.specious != partner.specious:
            raise Warning('In crossbreeding, the constraints follow the creature in which the event occurs.')

        self.obj = type(parent)(
            name=childName,
            initCoord=_mixTuple(parent.coord, partner.coord),
            initRotation=(parent.rotation+partner.rotation)/2,
            genome=(parent.genome*partner.genome).mutate(temp),
            specious=parent.specious,
            color=_mixTuple(parent.color, partner.color),
        )

    def notify(self):
        pass

    def shoot(self, ctx: TickContext):
        ctx.objects.append(self.obj)

@dataclass(frozen=True)
class ReproduceTrigger(Trigger):
    partner: Creature
    childName: str
    temp: float = 0.2

    def by(self, parent: Creature) -> Event:
        return ReproduceEvent(parent=parent, partner=self.partner, childName=self.childName, temp=self.temp)