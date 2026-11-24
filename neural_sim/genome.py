import genepy

GENOME = genepy.Genome.init(
    bodyGene=genepy.RectBodyGene.init(
        units=(
            genepy.PositiveUnit.fromValue('maxEnergy', 300, 50),
            genepy.PositiveUnit.fromValue('whRatio', 1, 0.5),
            genepy.PositiveUnit.fromValue('maxSpeed', 10, 2),
        )
    ),
    brainGene=genepy.NeuralBrainGene.init(),
    sensorGenes=[
        genepy.FoodVisionSensorGene.init(),
        genepy.CreatureVisionSensorGene.init()
    ]
)

SPECIOUS = genepy.Specious(
    name='NEURAL',
    constraints=[
        genepy.MovementConstraint(multiplier=0.5),
        genepy.UpkeepConstraint(),
        genepy.AttackConstraint(multiplier=0.1),
        genepy.ReproduceConstraint()
    ]
)