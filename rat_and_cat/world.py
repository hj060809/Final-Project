import genepy
import numpy as np
from rat import RAT_GENOME, RatBrain
from specious import RAT_SPECIOUS
from extinction_prevent import EXTICNTION_PREVENTION
from cat_gen_event import CAT_MATE_EVENT
import pickle

MAP_SIZE = (300, 300)

def cleaning(ctx: genepy.TickContext):
    return [genepy.SuicideEvent(o) for o in ctx.objects if isinstance(o, genepy.Food)]

SAVED = False
def save(ctx: genepy.TickContext):
    global SAVED
    if not SAVED:
        for i, o in enumerate(ctx.objects):
            if isinstance(o, genepy.Creature) and isinstance(o.brain, RatBrain):
                with open(f'rat_brains/random/b{i}.net', 'wb') as f:
                    pickle.dump(o.brain.net, f)
        SAVED = True

    return []

WORLD = genepy.World(
    width=MAP_SIZE[0],
    height=MAP_SIZE[1],
    initObjects=[
        *genepy.Scatter(
            generator=lambda i: genepy.creature.Creature(
                name=f'RAT_{i}',
                initCoord=(np.random.uniform(0, MAP_SIZE[0]), np.random.uniform(0, MAP_SIZE[1])),
                initRotation=np.random.uniform(0, 360),
                genome=RAT_GENOME.mutate(),
                specious=RAT_SPECIOUS,
                color=(120,120,120)
            ),
            count=10
        ).uniform(MAP_SIZE[0], MAP_SIZE[1]),
    ],
    eventSchedulers=[
        EXTICNTION_PREVENTION,
        CAT_MATE_EVENT,
        genepy.EventScheduler(
            action=cleaning,
            tickCondition=lambda t: True,
        ),
    ]
)