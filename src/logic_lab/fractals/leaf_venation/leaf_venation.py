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
    attractors: int
    length: float
    width: float
    step: float
    kill_distance: float
    max_distance: float
    hue: float


@dataclass
class Vein:
    position: py5.Py5Vector
    parent: Vein | None = None
    thickness: float = 1.0


PRESETS = [
    Preset("broad leaf", 8, 620, 590, 260, 4.4, 9, 54, 116),
    Preset("willow leaf", 19, 540, 650, 145, 4.0, 8, 48, 92),
    Preset("heart leaf", 29, 700, 560, 300, 4.2, 9, 58, 136),
]


class LeafVenation:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        self.base = py5.Py5Vector(width * 0.5, height * 0.82)
        self.tip = py5.Py5Vector(width * 0.5, height * 0.82 - preset.length)
        self.veins = [Vein(self.base, thickness=4.8)]
        self.attractors = self._make_attractors()

    def _leaf_radius_at(self, t: float) -> float:
        if self.preset.name == "willow leaf":
            return self.preset.width * py5.sin(py5.PI * t) ** 1.7
        if self.preset.name == "heart leaf":
            return self.preset.width * (py5.sin(py5.PI * t) ** 0.55) * (0.76 + 0.24 * t)
        return self.preset.width * py5.sin(py5.PI * t) ** 0.75

    def _make_attractors(self) -> list[py5.Py5Vector]:
        points = []
        while len(points) < self.preset.attractors:
            t = self.rng.uniform(0.03, 0.96)
            radius = self._leaf_radius_at(t)
            x = self.width * 0.5 + self.rng.uniform(-radius, radius)
            center_y = self.base.y + (self.tip.y - self.base.y) * t
            if abs(x - self.width * 0.5) > radius:
                continue
            y = center_y + self.rng.uniform(-6, 6)
            points.append(py5.Py5Vector(x, y))
        return points

    def update(self) -> None:
        if not self.attractors:
            return

        influences: dict[int, list[py5.Py5Vector]] = {}
        remaining = []

        for point in self.attractors:
            closest_index = -1
            closest_distance = self.preset.max_distance
            for i, vein in enumerate(self.veins):
                distance = vein.position.dist(point)
                if distance < self.preset.kill_distance:
                    closest_index = -1
                    closest_distance = 0
                    break
                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = i
            if closest_distance == 0:
                continue
            remaining.append(point)
            if closest_index >= 0:
                direction = point - self.veins[closest_index].position
                influences.setdefault(closest_index, []).append(direction.normalize())

        self.attractors = remaining
        new_veins = []
        for vein_index, directions in influences.items():
            vein = self.veins[vein_index]
            direction = py5.Py5Vector(0, 0)
            for item in directions:
                direction += item
            direction.normalize()
            new_position = vein.position + direction * self.preset.step
            new_veins.append(
                Vein(new_position, parent=vein, thickness=max(0.55, vein.thickness * 0.985))
            )
        self.veins.extend(new_veins)

    def draw_leaf_shape(self) -> None:
        py5.no_stroke()
        py5.fill(self.preset.hue, 24, 91, 46)
        py5.begin_shape()
        for i in range(80):
            t = i / 79
            y = self.base.y + (self.tip.y - self.base.y) * t
            x = self.width * 0.5 + self._leaf_radius_at(t)
            py5.vertex(x, y)
        for i in range(79, -1, -1):
            t = i / 79
            y = self.base.y + (self.tip.y - self.base.y) * t
            x = self.width * 0.5 - self._leaf_radius_at(t)
            py5.vertex(x, y)
        py5.end_shape(py5.CLOSE)

    def draw(self, show_attractors: bool) -> None:
        py5.background(48, 14, 96)
        self.draw_leaf_shape()
        py5.stroke_cap(py5.ROUND)

        py5.stroke(self.preset.hue - 18, 44, 42, 74)
        py5.stroke_weight(5.5)
        py5.line(self.base.x, self.base.y, self.tip.x, self.tip.y)

        for vein in self.veins:
            if vein.parent is None:
                continue
            py5.stroke(self.preset.hue + 8, 46, 36 + vein.thickness * 6, 78)
            py5.stroke_weight(vein.thickness)
            py5.line(
                vein.position.x, vein.position.y, vein.parent.position.x, vein.parent.position.y
            )

        if show_attractors:
            py5.no_stroke()
            py5.fill(34, 80, 86, 24)
            for point in self.attractors:
                py5.circle(point.x, point.y, 2.4)


venation: LeafVenation
preset_index = 0
show_attractors = False


def reset(index: int) -> None:
    global venation, preset_index
    preset_index = index % len(PRESETS)
    venation = LeafVenation(py5.width, py5.height, PRESETS[preset_index])


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    for _ in range(4):
        venation.update()
    venation.draw(show_attractors)


def key_pressed() -> None:
    global show_attractors
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "a":
        show_attractors = not show_attractors
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "leaf_venation_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
