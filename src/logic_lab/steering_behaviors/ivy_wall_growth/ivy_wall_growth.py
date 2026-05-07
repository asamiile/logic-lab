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
    tendrils: int
    branch_chance: float
    upward_bias: float
    hue: float


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    w: float
    h: float


@dataclass
class Tendril:
    position: py5.Py5Vector
    previous: py5.Py5Vector
    velocity: py5.Py5Vector
    age: int = 0
    alive: bool = True


PRESETS = [
    Preset("wall ivy", 13, 34, 0.018, -0.78, 122),
    Preset("window climber", 31, 28, 0.024, -0.62, 104),
    Preset("wild creeper", 57, 42, 0.032, -0.48, 86),
]

OBSTACLES = [
    Obstacle(290, 210, 220, 180),
    Obstacle(125, 500, 160, 130),
    Obstacle(575, 470, 135, 210),
]


class IvyWall:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        py5.noise_seed(preset.seed)
        self.tendrils = self._spawn_tendrils()

    def _spawn_tendrils(self) -> list[Tendril]:
        tendrils = []
        for _ in range(self.preset.tendrils):
            x = self.rng.uniform(self.width * 0.12, self.width * 0.88)
            y = self.height - self.rng.uniform(18, 70)
            position = py5.Py5Vector(x, y)
            velocity = py5.Py5Vector(self.rng.uniform(-0.7, 0.7), self.preset.upward_bias)
            tendrils.append(Tendril(position, py5.Py5Vector(x, y), velocity))
        return tendrils

    def _inside_obstacle(self, point: py5.Py5Vector) -> Obstacle | None:
        for obstacle in OBSTACLES:
            if (
                obstacle.x <= point.x <= obstacle.x + obstacle.w
                and obstacle.y <= point.y <= obstacle.y + obstacle.h
            ):
                return obstacle
        return None

    def _avoid_obstacles(self, point: py5.Py5Vector) -> py5.Py5Vector:
        force = py5.Py5Vector(0, 0)
        for obstacle in OBSTACLES:
            cx = min(max(point.x, obstacle.x), obstacle.x + obstacle.w)
            cy = min(max(point.y, obstacle.y), obstacle.y + obstacle.h)
            delta = point - py5.Py5Vector(cx, cy)
            distance = max(delta.mag, 0.001)
            if distance < 42:
                force += delta.normalize() * ((42 - distance) * 0.028)
        return force

    def update_and_draw(self) -> None:
        next_tendrils = []
        py5.stroke_cap(py5.ROUND)
        for tendril in self.tendrils:
            if not tendril.alive:
                continue
            tendril.previous = py5.Py5Vector(tendril.position.x, tendril.position.y)

            noise_angle = (
                py5.noise(tendril.position.x * 0.008, tendril.position.y * 0.008) * py5.TWO_PI
            )
            wander = py5.Py5Vector(py5.cos(noise_angle), py5.sin(noise_angle)) * 0.24
            cling = py5.Py5Vector(0, self.preset.upward_bias) * 0.08
            tendril.velocity += wander + cling + self._avoid_obstacles(tendril.position)
            if tendril.velocity.mag > 2.2:
                tendril.velocity.normalize()
                tendril.velocity *= 2.2

            tendril.position += tendril.velocity
            tendril.age += 1
            if self._inside_obstacle(tendril.position):
                tendril.position = tendril.previous
                tendril.velocity.rotate(self.rng.choice([-1, 1]) * 0.86)

            if (
                tendril.position.y < 24
                or tendril.position.x < 20
                or tendril.position.x > self.width - 20
            ):
                tendril.alive = False
                continue

            alpha = py5.remap(tendril.age, 0, 420, 72, 16)
            py5.stroke(self.preset.hue, 52, 34, alpha)
            py5.stroke_weight(py5.remap(tendril.age, 0, 420, 2.8, 0.7))
            py5.line(tendril.previous.x, tendril.previous.y, tendril.position.x, tendril.position.y)

            if tendril.age % 24 == 0:
                self._draw_leaf(tendril.position, tendril.velocity.heading)
            if (
                tendril.age > 32
                and self.rng.random() < self.preset.branch_chance
                and len(next_tendrils) < 18
            ):
                velocity = tendril.velocity.copy
                velocity.rotate(self.rng.choice([-1, 1]) * self.rng.uniform(0.45, 0.9))
                next_tendrils.append(
                    Tendril(
                        py5.Py5Vector(tendril.position.x, tendril.position.y),
                        py5.Py5Vector(tendril.position.x, tendril.position.y),
                        velocity,
                        age=max(0, tendril.age - 38),
                    )
                )
            next_tendrils.append(tendril)
        self.tendrils = next_tendrils[-260:]

    def _draw_wall(self) -> None:
        py5.background(43, 8, 93)
        py5.no_stroke()
        for obstacle in OBSTACLES:
            py5.fill(36, 9, 82, 95)
            py5.rect(obstacle.x, obstacle.y, obstacle.w, obstacle.h, 3)
            py5.fill(45, 8, 96, 60)
            py5.rect(obstacle.x + 10, obstacle.y + 10, obstacle.w - 20, obstacle.h - 20, 2)

    def _draw_leaf(self, position: py5.Py5Vector, angle: float) -> None:
        py5.push_matrix()
        py5.translate(position.x, position.y)
        py5.rotate(angle + self.rng.uniform(-0.9, 0.9))
        py5.no_stroke()
        py5.fill(self.preset.hue + self.rng.uniform(-14, 18), 54, 58, 62)
        size = self.rng.uniform(8, 18)
        py5.begin_shape()
        py5.vertex(0, 0)
        py5.bezier_vertex(size * 0.5, -size * 0.35, size * 0.5, -size * 1.0, 0, -size * 1.25)
        py5.bezier_vertex(-size * 0.5, -size * 1.0, -size * 0.5, -size * 0.35, 0, 0)
        py5.end_shape(py5.CLOSE)
        py5.pop_matrix()


ivy: IvyWall
preset_index = 0


def reset(index: int) -> None:
    global ivy, preset_index
    preset_index = index % len(PRESETS)
    ivy = IvyWall(py5.width, py5.height, PRESETS[preset_index])
    ivy._draw_wall()


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    py5.no_stroke()
    py5.fill(43, 8, 93, 3)
    py5.rect(0, 0, py5.width, py5.height)
    ivy.update_and_draw()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ivy_wall_growth_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
