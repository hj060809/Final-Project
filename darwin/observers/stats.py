import statistics
from typing import TYPE_CHECKING, Callable

import matplotlib
matplotlib.use('Agg')          # 반드시 pyplot import보다 먼저
import matplotlib.pyplot as plt
import pygame

from ..creatures import Specious
from ..simulator import Observer
from ..creatures import Creature

if TYPE_CHECKING:
    from ..simulator import Simulator

class StatisticalViewer(Observer):
    DPI = 100

    def __init__(
            self,
            specious: Specious,
            traits: dict[str, Callable[[Creature], float]],
            sampleEvery: int = 10,
            live: bool = True,
            window: tuple[int, int] | None = None,      # None이면 화면에 맞춰 자동
            drawOnSkip: bool = False,
        ):
        super().__init__(drawOnSkip=drawOnSkip)
        self.specious = specious
        self.traits = traits
        self.sampleEvery = sampleEvery
        self.live = live

        self.frames: list[int] = []
        self.population: list[int] = []
        self.mean = {name: [] for name in traits}
        self.std = {name: [] for name in traits}

        if window is None:
            window = self._fitToScreen(rows=len(traits) + 1)
        w, h = window

        self.fig, axes = plt.subplots(
            len(traits) + 1, 1, sharex=True,
            figsize=(w / self.DPI, h / self.DPI), dpi=self.DPI,
        )
        self.axes = list(axes)

        if live:
            self.window = pygame.Window('Darwin Stats', (w, h))

        self._ticks = 0
        self._dirty = False
        self.times: list[float] = []

    def _fitToScreen(self, rows: int) -> tuple[int, int]:
        pygame.init()
        screenW, screenH = pygame.display.get_desktop_sizes()[0]
        h = min(rows * 220, int(screenH * 0.85))         # 화면 높이의 85%까지
        w = min(700, int(screenW * 0.45))
        return w, h
    
    def onTick(self, simulator: Simulator):
        self._ticks += 1
        if self._ticks % self.sampleEvery:
            return

        creatures = [o for o in simulator.world._objects
                    if isinstance(o, Creature) and o.specious is self.specious]
        self.times.append(self._ticks * simulator.timeUnit)
        self.population.append(len(creatures))
        for name, extract in self.traits.items():
            values = [extract(c) for c in creatures]
            self.mean[name].append(statistics.fmean(values) if values else float('nan'))
            self.std[name].append(statistics.pstdev(values) if len(values) > 1 else 0.0)
        self._dirty = True

    def onFrame(self, simulator: Simulator):
        pygame.event.pump()                  # 창이 응답 상태를 유지하도록
        if self.live and self._dirty:
            self._show()
            self._dirty = False

    def _show(self):
        self.redraw()
        self.fig.canvas.draw()
        w, h = self.fig.canvas.get_width_height()
        image = pygame.image.frombuffer(self.fig.canvas.buffer_rgba(), (w, h), 'RGBA')
        self.window.get_surface().blit(image, (0, 0))
        self.window.flip()

    def redraw(self):
        ax = self.axes[0]
        ax.clear()
        ax.plot(self.times, self.population, color='tab:gray')
        ax.set_ylabel('population')

        for ax, name in zip(self.axes[1:], self.traits):
            m, s = self.mean[name], self.std[name]
            ax.clear()
            ax.plot(self.times, m, color='tab:blue')
            ax.fill_between(self.times, [a - b for a, b in zip(m, s)], [a + b for a, b in zip(m, s)],
                            color='tab:blue', alpha=0.2)
            ax.set_ylabel(name)

        self.axes[-1].set_xlabel('time (s)')
        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

    def save(self, path: str):
        self.redraw()
        self.fig.savefig(path, dpi=100)
