from specious import RAT_SPECIOUS
from extinction_prevent import score
from genepy import EventScheduler, TickContext, SuicideEvent
from genepy.creatures import Creature

MAX_N = 100

def _rat(objects) -> list[Creature]:
    return [o for o in objects if isinstance(o, Creature) and o.specious == RAT_SPECIOUS]

def kill(ctx: TickContext) -> list[SuicideEvent]:
    creatures = _rat(ctx.objects)
    count = max(0, len(creatures)-MAX_N)

    creatures.sort(key=score)

    return [SuicideEvent(c) for c in creatures[:count]]

OVERCROWDING_PREVENTION = EventScheduler(
    action=kill,
    objCondition=lambda objects: len(_rat(objects)) > MAX_N,
)