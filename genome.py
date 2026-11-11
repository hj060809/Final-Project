import darwin

GENOME = darwin.Genome.init(
    bodyGene=darwin.RectBodyGene.init(
        units=(
            darwin.PositiveUnit.fromValue('maxEnergy', 300, 50),
            darwin.PositiveUnit.fromValue('whRatio', 1, 0.5),
            darwin.PositiveUnit.fromValue('maxSpeed', 10, 2),
        )
    ),
    brainGene=darwin.NeuralBrainGene.init(),
    sensorGenes=[
        darwin.FoodVisionSensorGene.init(),
        darwin.CreatureVisionSensorGene.init()
    ]
)

SPECIOUS = darwin.Specious(
    name='NEURAL',
    constraints=[
        darwin.MovementConstraint(multiplier=0.5),
        darwin.UpkeepConstraint(),
        darwin.AttackConstraint(multiplier=0.1),
        darwin.ReproduceConstraint()
    ]
)