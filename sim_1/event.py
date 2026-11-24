import itertools
import random

from genepy import EventScheduler, TickContext, GenEvent
from genepy.creatures import Creature
from genepy.objects import Food

FN = 3
FEED_COUNT = 5
FOOD_ENERGY = 50
FOOD_RADIUS = 1.5

SIZEN = 1000
MATE_RATIO = 0.1     # 전체 쌍 중 교배할 비율 (0~1)


_childIds = itertools.count()

def _mix(t1: tuple[float, ...], t2: tuple[float, ...]) -> tuple[float, ...]:
    return tuple((a + b) / 2 for a, b in zip(t1, t2))

def _creatures(objects) -> list[Creature]:
    return [o for o in objects if isinstance(o, Creature)]

def _foods(objects) -> list[Food]:
    return [o for o in objects if isinstance(o, Food)]

def mate(ctx: TickContext) -> list[GenEvent]:
    pairs = list(itertools.combinations(_creatures(ctx.objects), 2))
    matablePairs = [p for p in pairs if p[0].specious == p[1].specious]
    matablePairs.sort(key=lambda c: c[0].energy/c[0]._maxEnergy+c[1].energy/c[1]._maxEnergy, reverse=True)
    
    count = round(len(matablePairs) * MATE_RATIO)

    count = min(max(1, count), len(matablePairs))

    events = []
    for a, b in matablePairs[:count]:
        events.append(GenEvent(
            type(a),
            name=f'C_{next(_childIds)}',
            initCoord=(random.uniform(0, ctx.width), random.uniform(0, ctx.height)),
            initRotation=random.uniform(0, 360),
            genome=(a.genome * b.genome).mutate(),
            specious=a.specious,
            color=_mix(a.color, b.color),
        ))
    return events

_foodIds = itertools.count()

def feed(ctx: TickContext) -> list[GenEvent]:
    return [
        GenEvent(
            Food,
            name=f'Food_{next(_foodIds)}',
            energy=FOOD_ENERGY,
            radius=FOOD_RADIUS,
            initCoord=(random.uniform(0, ctx.width), random.uniform(0, ctx.height)),
        )
        for _ in range(FEED_COUNT)
    ]


FEED_EVENT = EventScheduler(
    action=feed,
    objCondition=lambda objects: len(_foods(objects)) <= FN,
)

MATE_EVENT = EventScheduler(
    action=mate,
    objCondition=lambda objects: sum(c.body.size for c in _creatures(objects)) <= SIZEN,
)
