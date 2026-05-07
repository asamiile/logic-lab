from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Preset:
    name: str
    seed: int
    cell_size: int
    moisture_scale: float
    spread_bias: float
    decay: float
    hue: float


PRESETS = [
    Preset("soft moss", 11, 5, 0.042, 0.32, 0.004, 118),
    Preset("lichen islands", 28, 5, 0.026, 0.22, 0.002, 78),
    Preset("forest floor", 43, 4, 0.058, 0.38, 0.006, 142),
]


class MossColony:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.cols = width // preset.cell_size
        self.rows = height // preset.cell_size
        self.rng = Random(preset.seed)
        py5.noise_seed(preset.seed)
        self.cells = [[0.0 for _ in range(self.cols)] for _ in range(self.rows)]
        self._seed_colonies()

    def _seed_colonies(self) -> None:
        for _ in range(22):
            cx = self.rng.randrange(4, self.cols - 4)
            cy = self.rng.randrange(4, self.rows - 4)
            radius = self.rng.randrange(2, 7)
            for y in range(max(0, cy - radius), min(self.rows, cy + radius + 1)):
                for x in range(max(0, cx - radius), min(self.cols, cx + radius + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius:
                        self.cells[y][x] = self.rng.uniform(0.48, 0.92)

    def update(self) -> None:
        next_cells = [[0.0 for _ in range(self.cols)] for _ in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.cols):
                moisture = py5.noise(x * self.preset.moisture_scale, y * self.preset.moisture_scale)
                neighborhood = 0.0
                neighbors = 0
                for oy in (-1, 0, 1):
                    for ox in (-1, 0, 1):
                        if ox == 0 and oy == 0:
                            continue
                        nx = x + ox
                        ny = y + oy
                        if 0 <= nx < self.cols and 0 <= ny < self.rows:
                            neighborhood += self.cells[ny][nx]
                            neighbors += 1
                average = neighborhood / max(neighbors, 1)
                value = self.cells[y][x]
                growth = average * (moisture + self.preset.spread_bias) * 0.095
                spores = 0.18 if self.rng.random() < 0.0009 and moisture > 0.42 else 0.0
                next_cells[y][x] = min(1.0, max(0.0, value + growth + spores - self.preset.decay))
        self.cells = next_cells

    def draw(self) -> None:
        py5.background(40, 13, 94)
        py5.no_stroke()
        size = self.preset.cell_size
        for y, row in enumerate(self.cells):
            for x, value in enumerate(row):
                if value < 0.035:
                    continue
                moisture = py5.noise(x * self.preset.moisture_scale, y * self.preset.moisture_scale)
                hue = self.preset.hue + py5.remap(moisture, 0, 1, -28, 22)
                brightness = py5.remap(value, 0, 1, 28, 78)
                alpha = py5.remap(value, 0, 1, 10, 78)
                py5.fill(hue, 42 + value * 32, brightness, alpha)
                wobble = py5.remap(moisture, 0, 1, -1.2, 1.8)
                py5.circle(
                    x * size + size * 0.5,
                    y * size + size * 0.5,
                    size * (0.72 + value + wobble * 0.1),
                )


colony: MossColony
preset_index = 0


def reset(index: int) -> None:
    global colony, preset_index
    preset_index = index % len(PRESETS)
    colony = MossColony(py5.width, py5.height, PRESETS[preset_index])


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    for _ in range(2):
        colony.update()
    colony.draw()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "moss_colony_growth_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
