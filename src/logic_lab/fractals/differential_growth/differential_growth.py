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
    radius: float
    split_distance: float
    repel_distance: float
    attraction: float
    repulsion: float
    noise_amount: float
    hue: float


PRESETS = [
    Preset("ruffled leaf", 16, 145, 13, 30, 0.018, 0.95, 0.34, 112),
    Preset("coral edge", 25, 118, 10, 24, 0.012, 1.28, 0.55, 18),
    Preset("cell membrane", 41, 160, 16, 36, 0.024, 0.72, 0.22, 184),
]


class DifferentialGrowth:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        self.center = py5.Py5Vector(width * 0.5, height * 0.5)
        self.points = self._initial_loop()

    def _initial_loop(self) -> list[py5.Py5Vector]:
        points = []
        count = 52
        for i in range(count):
            a = py5.TWO_PI * i / count
            wobble = 1.0 + 0.06 * py5.sin(a * 5 + self.preset.seed)
            points.append(
                py5.Py5Vector(
                    self.center.x + py5.cos(a) * self.preset.radius * wobble,
                    self.center.y + py5.sin(a) * self.preset.radius * wobble,
                )
            )
        return points

    def update(self) -> None:
        forces = [py5.Py5Vector(0, 0) for _ in self.points]

        for i, point in enumerate(self.points):
            prev_point = self.points[i - 1]
            next_point = self.points[(i + 1) % len(self.points)]
            target = (prev_point + next_point) * 0.5
            forces[i] += (target - point) * self.preset.attraction

        for i, point in enumerate(self.points):
            for j in range(i + 1, len(self.points)):
                other = self.points[j]
                delta = point - other
                distance = max(delta.mag, 0.001)
                if distance < self.preset.repel_distance:
                    push = delta.normalize() * ((self.preset.repel_distance - distance) / distance)
                    forces[i] += push * self.preset.repulsion
                    forces[j] -= push * self.preset.repulsion

        for i, point in enumerate(self.points):
            outward = point - self.center
            if outward.mag > 0:
                outward.normalize()
                forces[i] += outward * self.preset.noise_amount * self.rng.uniform(0.3, 1.0)
            point += forces[i]

        self._split_long_edges()

    def _split_long_edges(self) -> None:
        expanded = []
        for i, point in enumerate(self.points):
            next_point = self.points[(i + 1) % len(self.points)]
            expanded.append(point)
            if point.dist(next_point) > self.preset.split_distance and len(self.points) < 720:
                midpoint = (point + next_point) * 0.5
                expanded.append(midpoint)
        self.points = expanded

    def draw(self) -> None:
        py5.background(44, 9, 96)
        py5.no_fill()
        py5.stroke_cap(py5.ROUND)

        for offset, alpha in [(12, 10), (6, 18), (0, 82)]:
            py5.stroke(self.preset.hue + offset, 52, 42 + offset, alpha)
            py5.stroke_weight(1.4 + offset * 0.09)
            py5.begin_shape()
            for point in self.points:
                py5.curve_vertex(point.x, point.y)
            for point in self.points[:3]:
                py5.curve_vertex(point.x, point.y)
            py5.end_shape()


growth: DifferentialGrowth
preset_index = 0


def reset(index: int) -> None:
    global growth, preset_index
    preset_index = index % len(PRESETS)
    growth = DifferentialGrowth(py5.width, py5.height, PRESETS[preset_index])


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    for _ in range(2):
        growth.update()
    growth.draw()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "differential_growth_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
