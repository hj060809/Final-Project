import itertools
import random
import math

from specious import RAT_SPECIOUS
from genepy import EventScheduler, TickContext, GenEvent
from genepy.creatures import Creature

MAX_N = 50
MIN_N = 25
MAX_CHILD = 2

_childIds = itertools.count()

def _rat(objects) -> list[Creature]:
    return [o for o in objects if isinstance(o, Creature) and o.specious == RAT_SPECIOUS]

def score(c: Creature) -> float:
    return c.age*c.energy/c._maxEnergy

def mate(ctx: TickContext) -> list[GenEvent]:
    creatures = _rat(ctx.objects)
    count = max(1, MAX_N-len(creatures))

    creatures.sort(key=score, reverse=True)

    events = []
    for c in creatures:
        for _ in range(MAX_CHILD):
            events.append(GenEvent(
                type(c),
                name=f'C_{next(_childIds)}',
                initCoord=(random.uniform(0, ctx.width), random.uniform(0, ctx.height)),
                initRotation=random.uniform(0, 360),
                genome=c.genome.mutate(),
                specious=c.specious,
                color=c.color,
            ))
            count -= 1
            if count <= 0 : break
        if count <= 0 : break
    return events

EXTICNTION_PREVENTION = EventScheduler(
    action=mate,
    objCondition=lambda objects: len(_rat(objects)) <= MIN_N,
)