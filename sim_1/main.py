import darwin
import numpy as np
from sim_1.event import FEED_EVENT, MATE_EVENT
import time

"""

확장 가능한 것

viewer
새 SensorGene 만들기 + 새 Sensor 만들기
새 BodyGene 만들기 + 새 Body 만들기
새 BrainGene 만들기 + 새 Brain 만들기

"""

TPS = 60
mapSize = (300, 300)

PREY_SPECIOUS = darwin.Specious(
    name='prey',
    constraints=darwin.CONSTRAINT_PACK
)

PREY_GENOME1 = darwin.Genome.init(
    bodyGene=darwin.RectBodyGene.init(
        units=(
            darwin.PositiveUnit.fromValue('maxEnergy', 300, 50),
            darwin.PositiveUnit.fromValue('whRatio', 1, 0.5),
            darwin.PositiveUnit.fromValue('maxSpeed', 10, 2),
        )
    ),
    brainGene=darwin.RuleBrainGene.init(
        units=(
            darwin.ProbUnit.fromValue('hostility', 0.3, 0.1),
            darwin.ProbUnit.fromValue('cowardice', 0.5, 0.1),
        )
    ),
    sensorGenes=[
        darwin.FoodVisionSensorGene.init(),
        darwin.CreatureVisionSensorGene.init()
    ]
)

world = darwin.World(
    width=mapSize[0],
    height=mapSize[1],
    initObjects=[
        *darwin.Scatter(
            generator=lambda i: darwin.creature.Creature(
                name=f'G_{i}',
                initCoord=(np.random.uniform(0, mapSize[0]), np.random.uniform(0, mapSize[1])),
                initRotation=np.random.uniform(0, 360),
                genome=PREY_GENOME1.mutate(),
                specious=PREY_SPECIOUS,
                color=(0,0,255)
            ),
            count=40
        ).uniform(mapSize[0], mapSize[1]),
    ],
    eventSchedulers=[FEED_EVENT, MATE_EVENT]
)
"""
        *darwin.Scatter(
            generator=lambda i: darwin.creature.Creature(
                name=f'P_{i}',
                initCoord=(np.random.uniform(0, mapSize[0]), np.random.uniform(0, mapSize[1])),
                initRotation=np.random.uniform(0, 360),
                genome=PREDATOR_GENOME.mutate(),
                specious=PREDATOR_SPECIOUS,
                color=(255,0,0)
            ),
            count=10
        ).uniform(mapSize[0], mapSize[1]),
        
        """

LOG_INTERVAL = 10.0    # 현실 시간(초)

lastTick = 0
skip = TPS*0

start = lastLog = time.perf_counter()
for i in range(skip):
    world.tick(1 / TPS)

    now = time.perf_counter()
    if now - lastLog >= LOG_INTERVAL:
        done = i + 1
        speed = (done - lastTick) / (now - lastLog)                  # 최근 구간 tick/s
        eta = (skip - done) / speed if speed > 0 else float('inf')

        print(
            f'[{now - start:7.1f}s] tick {done}/{skip} ({done / skip:6.2%}) '
            f'| sim {done / TPS / 60:6.1f}min | {speed:7.1f} tick/s | ETA {eta / 60:5.1f}min ',
            flush=True,
        )
        lastLog, lastTick = now, done

viewer = darwin.Viewer(window=(600, 600))

stats1 = darwin.StatisticalViewer(specious=PREY_SPECIOUS, traits={
    'maxSpeed':     lambda c: c.body.maxSpeed,
    'cowardice':     lambda c: c.brain.cowardice if isinstance(c.brain, darwin.RuleBrain) else 0.0,
    'creatureRange': lambda c: next((s.range for s in c.sensors if isinstance(s, darwin.CreatureVisionSensor)), 0.0),
    'hostility': lambda c: c.brain.hostility if isinstance(c.brain, darwin.RuleBrain) else 0.0,
})

sim = darwin.Simulator(world, tickPerSec=TPS, framePerTick=10)
sim.registerObserver(viewer)
sim.registerObserver(stats1)
sim.run()

"""
시야 범위를 raycasting으로 변경 -> obstacle에 걸리는 경우 제거
공격 번식 처리 (isAggressive 처리 해야 함)
event가 실패하는 경우 핸들링 (kill, eat 중복 -> 없는 obj를 찾음): 예외처리해서 event 효력 없애거나 그런 일 없도록 sim에서 스케쥴링
"""