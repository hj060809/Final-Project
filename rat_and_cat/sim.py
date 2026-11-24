from world import WORLD
from rat import RatBrain
from specious import RAT_SPECIOUS
from extinction_prevent import score
import genepy

TPS = 60

viewer = genepy.Viewer(window=(600, 600), drawOnSkip=False)

stats = genepy.StatisticalViewer(specious=RAT_SPECIOUS, traits={
    #'food vision range':     lambda c: next((s.range for s in c.sensors if isinstance(s, darwin.FoodVisionSensor)), 0.0),
    #'crt vision range':     lambda c: next((s.range for s in c.sensors if isinstance(s, darwin.CreatureVisionSensor)), 0.0),
    'energy Rate':         lambda c: c.energy/c.body.maxEnergy,
    'speed': lambda c: c.body.maxSpeed,
    'age':         lambda c: c.age,
    'score':         score,
}, drawOnSkip=True, history=120)

sim = genepy.Simulator(WORLD, tickPerSec=TPS, framePerTick=1)
sim.registerObserver(stats)
sim.registerObserver(viewer)

#sim.skip(second=2000, FRAME_INTERVAL=5)
sim.run()