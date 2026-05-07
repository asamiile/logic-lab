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
    root: tuple[float, float]
    bounds: tuple[float, float, float, float]
    attractor_count: int
    step_size: float
    kill_distance: float
    max_distance: float
    hue: float


@dataclass
class Node:
    x: float
    y: float
    parent: Node | None = None
    radius: float = 1.0


@dataclass
class Attractor:
    x: float
    y: float


PRESETS = [
    Preset("tree crown", 12, (0.5, 0.93), (0.12, 0.05, 0.88, 0.82), 520, 6.0, 12, 72, 92),
    Preset("leaf veins", 33, (0.5, 0.92), (0.18, 0.08, 0.82, 0.86), 640, 4.6, 9, 58, 118),
    Preset("root fan", 47, (0.5, 0.12), (0.08, 0.18, 0.92, 0.94), 580, 5.0, 11, 64, 78),
]


class SpaceColonization:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        self.nodes = [Node(width * preset.root[0], height * preset.root[1], radius=5.5)]
        self.attractors = self._generate_attractors()

    def _generate_attractors(self) -> list[Attractor]:
        left, top, right, bottom = self.preset.bounds
        attractors = []
        while len(attractors) < self.preset.attractor_count:
            x = self.rng.uniform(left * self.width, right * self.width)
            y = self.rng.uniform(top * self.height, bottom * self.height)
            if self.preset.name == "leaf veins" and not self._inside_leaf(x, y):
                continue
            attractors.append(Attractor(x, y))
        return attractors

    def _inside_leaf(self, x: float, y: float) -> bool:
        cx = self.width * 0.5
        cy = self.height * 0.48
        rx = self.width * 0.33
        ry = self.height * 0.42
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1.0

    def update(self) -> None:
        if not self.attractors:
            return

        influences: dict[int, list[tuple[float, float]]] = {}
        remaining = []

        for attractor in self.attractors:
            closest_index = -1
            closest_distance = self.preset.max_distance

            for i, node in enumerate(self.nodes):
                dx = attractor.x - node.x
                dy = attractor.y - node.y
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < self.preset.kill_distance:
                    closest_index = -1
                    closest_distance = 0
                    break
                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = i

            if closest_distance == 0:
                continue
            remaining.append(attractor)
            if closest_index >= 0:
                node = self.nodes[closest_index]
                dx = attractor.x - node.x
                dy = attractor.y - node.y
                length = max((dx * dx + dy * dy) ** 0.5, 0.001)
                influences.setdefault(closest_index, []).append((dx / length, dy / length))

        self.attractors = remaining

        if not influences and self.attractors:
            closest_node_index = 0
            closest_attractor = self.attractors[0]
            closest_distance = float("inf")
            for i, node in enumerate(self.nodes):
                for attractor in self.attractors:
                    dx = attractor.x - node.x
                    dy = attractor.y - node.y
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_node_index = i
                        closest_attractor = attractor
            node = self.nodes[closest_node_index]
            direction = py5.Py5Vector(closest_attractor.x - node.x, closest_attractor.y - node.y)
            if direction.mag > 0:
                influences[closest_node_index] = [direction.normalize()]

        new_nodes = []
        for node_index, vectors in influences.items():
            node = self.nodes[node_index]
            dx = sum(v[0] for v in vectors) / len(vectors)
            dy = sum(v[1] for v in vectors) / len(vectors)
            length = max((dx * dx + dy * dy) ** 0.5, 0.001)
            jitter = py5.radians(self.rng.uniform(-5, 5))
            ndx = (dx / length) * py5.cos(jitter) - (dy / length) * py5.sin(jitter)
            ndy = (dx / length) * py5.sin(jitter) + (dy / length) * py5.cos(jitter)
            child = Node(
                node.x + ndx * self.preset.step_size,
                node.y + ndy * self.preset.step_size,
                parent=node,
                radius=max(0.7, node.radius * 0.985),
            )
            new_nodes.append(child)

        self.nodes.extend(new_nodes)

    def draw(self, show_attractors: bool) -> None:
        py5.background(42, 13, 96)
        py5.stroke_cap(py5.ROUND)

        for node in self.nodes:
            if node.parent is None:
                continue
            depth = 1.0 - min(node.radius / 5.5, 1.0)
            py5.stroke(self.preset.hue + depth * 24, 48, 34 + depth * 33, 78)
            py5.stroke_weight(node.radius)
            py5.line(node.x, node.y, node.parent.x, node.parent.y)

        if show_attractors:
            py5.no_stroke()
            py5.fill(36, 70, 90, 28)
            for attractor in self.attractors:
                py5.circle(attractor.x, attractor.y, 2.6)


colonization: SpaceColonization
preset_index = 0
show_attractors = False


def reset(index: int) -> None:
    global colonization, preset_index
    preset_index = index % len(PRESETS)
    colonization = SpaceColonization(py5.width, py5.height, PRESETS[preset_index])


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    for _ in range(4):
        colonization.update()
    colonization.draw(show_attractors)


def key_pressed() -> None:
    global show_attractors
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "a":
        show_attractors = not show_attractors
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "space_colonization_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
