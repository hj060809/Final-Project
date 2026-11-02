import darwin
import numpy as np

"""

확장 가능한 것

viewer
새 SensorGene 만들기 + 새 Sensor 만들기
새 BodyGene 만들기 + 새 Body 만들기
새 BrainGene 만들기 + 새 Brain 만들기

"""

mapSize = (100, 100)

genome = darwin.Genome.init(
    bodyGene=darwin.RectBodyGene.init(
        units=(
            darwin.PositiveUnit.fromValue('health', 5, 0.001),
            darwin.PositiveUnit.fromValue('width', 5, 0.5),
            darwin.PositiveUnit.fromValue('height', 5, 0.5),
            darwin.PositiveUnit.fromValue('maxSpeed', 10, 2),
        )
    ),
    brainGene=darwin.RuleBrainGene.init(),
    sensorGenes=[
        darwin.FoodVisionSensorGene.init()
    ]
)

world = darwin.WorldState(
    width=mapSize[0],
    height=mapSize[1],
    objects=[
        *darwin.Scatter(
            generator=lambda i: darwin.objects.Food(
                name=f"Food_{i}", 
                energy=10, 
                size=1.5, 
                initCoord=(np.random.uniform(0, mapSize[0]), np.random.uniform(0, mapSize[1]))
            ),
            density=0.01
        ).uniform(mapSize[0], mapSize[1]),
        *darwin.Scatter(
            generator=lambda i: darwin.creature.Creature(
                name=f'G_{i}',
                initCoord=(np.random.uniform(0, mapSize[0]), np.random.uniform(0, mapSize[1])),
                initRotation=np.random.uniform(0, 360),
                genome=genome.mutate(),
                color=(0,0,255)
            ),
            count=10
        ).uniform(mapSize[0], mapSize[1]),
        darwin.Obstacle(
            name='O',
            width=mapSize[0]/2,
            height=3,
            initCoord=(mapSize[0]/2, mapSize[1]/2),
        )
    ]
)

sim = darwin.Simulator(world)

viewer = darwin.Viewer(window=(600, 600))
viewer.run(sim)