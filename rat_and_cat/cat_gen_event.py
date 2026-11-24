import itertools
import random

from cat import CAT_GENOME
from specious import CAT_SPECIOUS
from genepy import EventScheduler, TickContext, GenEvent
from genepy.creatures import Creature

N = 10

_childIds = itertools.count()

def _cat(objects) -> list[Creature]:
    return [o for o in objects if isinstance(o, Creature) and o.specious == CAT_SPECIOUS]

def mate(ctx: TickContext) -> list[GenEvent]:
    count = N-len(_cat(ctx.objects))

    events = []
    for _ in range(count):
        events.append(GenEvent(
            Creature,
            name=f'C_{next(_childIds)}',
            initCoord=(random.uniform(0, ctx.width), random.uniform(0, ctx.height)),
            initRotation=random.uniform(0, 360),
            genome=CAT_GENOME,
            specious=CAT_SPECIOUS,
            color=(255, 0, 0)
        ))
    return events

CAT_MATE_EVENT = EventScheduler(
    action=mate,
    objCondition=lambda objects: len(_cat(objects)) <= N,
)