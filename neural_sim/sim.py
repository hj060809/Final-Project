from neural_sim.world import WORLD
from neural_sim.genome import SPECIOUS
import genepy

TPS = 60

viewer = genepy.Viewer(window=(600, 600), drawOnSkip=False)

stats = genepy.StatisticalViewer(specious=SPECIOUS, traits={
    'energyRatio':     lambda c: c.energy/c._maxEnergy,
    'size':         lambda c: c.body.size,
    'eatWill':     lambda c: c.brain._eatWill if isinstance(c.brain, genepy.NeuralBrain) else 0.0,
    'attackWill':     lambda c: c.brain._attackWill if isinstance(c.brain, genepy.NeuralBrain) else 0.0,
}, drawOnSkip=True)

sim = genepy.Simulator(WORLD, tickPerSec=TPS, framePerTick=5)
sim.registerObserver(stats)
sim.registerObserver(viewer)

sim.skip(second=300, FRAME_INTERVAL=5)
sim.run()