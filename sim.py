from world import WORLD, TPS
from genome import SPECIOUS
import darwin

viewer = darwin.Viewer(window=(600, 600), drawOnSkip=False)

stats = darwin.StatisticalViewer(specious=SPECIOUS, traits={
    'WH ratio':     lambda c: c.body.whRatio if isinstance(c.body, darwin.RectBody) else 0.0,
    'size':         lambda c: c.body.size,
    'eatWill':     lambda c: c.brain._eatWill if isinstance(c.brain, darwin.NeuralBrain) else 0.0,
    'attackWill':     lambda c: c.brain._attackWill if isinstance(c.brain, darwin.NeuralBrain) else 0.0,
}, drawOnSkip=True)

sim = darwin.Simulator(WORLD, tickPerSec=TPS, framePerTick=10)
sim.registerObserver(stats)
sim.registerObserver(viewer)

sim.skip(second=30, FRAME_INTERVAL=5)
sim.run()