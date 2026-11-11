from ..simulator import Observer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..simulator import Simulator

class Recorder(Observer):
    def __init__(self, drawOnSkip: bool = False):
        super().__init__(drawOnSkip=drawOnSkip)
        pass

    def onTick(self, simulator: Simulator):
        pass

    def onFrame(self, simulator: Simulator):
        pass