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
    count: int
    start_y: float
    noise_scale: float
    curl_strength: float
    speed: float
    hue: float


@dataclass
class Vine:
    position: py5.Py5Vector
    previous: py5.Py5Vector
    age: int = 0


PRESETS = [
    Preset("climbing vines", 12, 135, 0.92, 0.006, 1.8, 2.2, 116),
    Preset("wind grass", 25, 220, 0.88, 0.009, 1.25, 1.75, 82),
    Preset("root hairs", 39, 180, 0.12, 0.007, 1.65, 1.95, 44),
]


class CurlNoiseVines:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        py5.noise_seed(preset.seed)
        self.vines = self._spawn_vines()

    def _spawn_vines(self) -> list[Vine]:
        vines = []
        y = self.height * self.preset.start_y
        for _ in range(self.preset.count):
            x = self.rng.uniform(self.width * 0.08, self.width * 0.92)
            jittered_y = y + self.rng.uniform(-24, 24)
            position = py5.Py5Vector(x, jittered_y)
            vines.append(Vine(position, py5.Py5Vector(position.x, position.y)))
        return vines

    def _field_angle(self, x: float, y: float) -> float:
        s = self.preset.noise_scale
        eps = 0.012
        n1 = py5.noise(x * s + eps, y * s)
        n2 = py5.noise(x * s - eps, y * s)
        n3 = py5.noise(x * s, y * s + eps)
        n4 = py5.noise(x * s, y * s - eps)
        dx = n1 - n2
        dy = n3 - n4
        return py5.atan2(dx, -dy) * self.preset.curl_strength

    def update_and_draw(self) -> None:
        py5.stroke_cap(py5.ROUND)
        for vine in self.vines:
            vine.previous = py5.Py5Vector(vine.position.x, vine.position.y)
            angle = self._field_angle(vine.position.x, vine.position.y)
            if self.preset.name == "root hairs":
                angle += py5.HALF_PI
            else:
                angle -= py5.HALF_PI * 0.7

            velocity = py5.Py5Vector(py5.cos(angle), py5.sin(angle)) * self.preset.speed
            vine.position += velocity
            vine.age += 1

            if (
                vine.position.x < -20
                or vine.position.x > self.width + 20
                or vine.position.y < -20
                or vine.position.y > self.height + 20
                or vine.age > 520
            ):
                vine.position = py5.Py5Vector(
                    self.rng.uniform(self.width * 0.08, self.width * 0.92),
                    self.height * self.preset.start_y + self.rng.uniform(-20, 20),
                )
                vine.previous = py5.Py5Vector(vine.position.x, vine.position.y)
                vine.age = 0
                continue

            alpha = py5.remap(vine.age, 0, 520, 72, 8)
            hue = self.preset.hue + py5.sin(vine.age * 0.022) * 18
            py5.stroke(hue, 48, 38 + py5.sin(vine.age * 0.04) * 8, alpha)
            py5.stroke_weight(py5.remap(vine.age, 0, 520, 2.6, 0.45))
            py5.line(vine.previous.x, vine.previous.y, vine.position.x, vine.position.y)

            if vine.age % 62 == 0 and self.rng.random() < 0.55:
                self._draw_leaf(vine.position, angle)

    def _draw_leaf(self, position: py5.Py5Vector, angle: float) -> None:
        py5.push_matrix()
        py5.translate(position.x, position.y)
        py5.rotate(angle + self.rng.uniform(-0.8, 0.8))
        py5.no_stroke()
        py5.fill(self.preset.hue + 24, 42, 64, 42)
        size = self.rng.uniform(7, 15)
        py5.ellipse(0, -size * 0.45, size * 0.55, size)
        py5.pop_matrix()


vines: CurlNoiseVines
preset_index = 0


def reset(index: int) -> None:
    global vines, preset_index
    preset_index = index % len(PRESETS)
    vines = CurlNoiseVines(py5.width, py5.height, PRESETS[preset_index])
    py5.background(48, 15, 96)


def setup() -> None:
    py5.size(900, 900)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    py5.no_stroke()
    py5.fill(48, 15, 96, 5)
    py5.rect(0, 0, py5.width, py5.height)
    vines.update_and_draw()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "curl_noise_vines_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
