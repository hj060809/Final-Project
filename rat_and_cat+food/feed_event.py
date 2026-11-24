import itertools
import random

from genepy import EventScheduler, TickContext, GenEvent
from genepy.objects import Food

MIN_FOOD = 40
FEED_COUNT = 100
FOOD_ENERGY = 50
FOOD_RADIUS = 1.5

_foodIds = itertools.count()

def _foods(objects) -> list[Food]:
    return [o for o in objects if isinstance(o, Food)]

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
    objCondition=lambda objects: len(_foods(objects)) <= MIN_FOOD,
)