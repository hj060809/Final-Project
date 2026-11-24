import genepy
import numpy as np
from neural_sim.genome import GENOME, SPECIOUS
from neural_sim.event import FEED_EVENT, MATE_EVENT

MAP_SIZE = (300, 300)

WORLD = genepy.World(
    width=MAP_SIZE[0],
    height=MAP_SIZE[1],
    initObjects=[
        *genepy.Scatter(
            generator=lambda i: genepy.creature.Creature(
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