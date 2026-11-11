import darwin
import numpy as np
from genome import GENOME, SPECIOUS
from event import FEED_EVENT, MATE_EVENT

TPS = 60
MAP_SIZE = (300, 300)

WORLD = darwin.World(
    width=MAP_SIZE[0],
    height=MAP_SIZE[1],
    initObjects=[
        *darwin.Scatter(
            generator=lambda i: darwin.creature.Creature(
                name=f'NEURAL_CREATURE_{i}',
                initCoord=(np.random.uniform(0, MAP_SIZE[0]), np.random.uniform(0, MAP_SIZE[1])),
                initRotation=np.random.uniform(0, 360),
                genome=GENOME.mutate(),
                specious=SPECIOUS,
                color=(255,0,0)
            ),
            count=40
        ).uniform(MAP_SIZE[0], MAP_SIZE[1]),
    ],
    eventSchedulers=[FEED_EVENT, MATE_EVENT]
)