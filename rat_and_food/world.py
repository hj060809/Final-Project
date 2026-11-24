import genepy
import numpy as np
from rat import RAT_GENOME
from specious import RAT_SPECIOUS
from extinction_prevent import EXTICNTION_PREVENTION
from feed_event import FEED_EVENT
from kill_event import OVERCROWDING_PREVENTION

MAP_SIZE = (500, 500)

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
    eventSchedulers=[EXTICNTION_PREVENTION, FEED_EVENT, OVERCROWDING_PREVENTION]
)