from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

STEP = 6
MAX_RIPPLES = 9
ripples: list[Ripple] = []


@dataclass
class Ripple:
    x: float
    y: float
    age: float
    hue: float

    def update(self) -> None:
        self.age += 1.0

    def amplitude_at(self, x: float, y: float) -> float:
        distance = math.hypot(x - self.x, y - self.y)
        radius = self.age * 4.2
        envelope = math.exp(-abs(distance - radius) * 0.035) * math.exp(-self.age * 0.012)
        return math.sin(distance * 0.18 - self.age * 0.42) * envelope


def setup() -> None:
    py5.size(720, 420)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        add_ripple(
            py5.width * (0.18 + i * 0.16),
            py5.height * (0.38 + 0.22 * math.sin(i * 1.7)),
        )


def add_ripple(x: float, y: float) -> None:
    ripples.append(Ripple(x, y, 0.0, (190 + len(ripples) * 31) % 360))
    if len(ripples) > MAX_RIPPLES:
        ripples.pop(0)


def draw() -> None:
    py5.background(214, 28, 10)
    py5.no_stroke()

    for y in range(0, py5.height, STEP):
        for x in range(0, py5.width, STEP):
            height = sum(ripple.amplitude_at(x, y) for ripple in ripples)
            brightness = py5.constrain(42 + height * 90, 8, 94)
            hue = 198 + height * 24
            py5.fill(hue, 62, brightness, 88)
            py5.rect(x, y, STEP + 1, STEP + 1)

    py5.no_fill()
    for ripple in ripples:
        py5.stroke(ripple.hue, 55, 95, max(0, 52 - ripple.age * 0.5))
        py5.stroke_weight(1.4)
        py5.circle(ripple.x, ripple.y, ripple.age * 8.4)
        ripple.update()

    if py5.frame_count % 96 == 0:
        add_ripple(py5.random(70, py5.width - 70), py5.random(70, py5.height - 70))


def mouse_pressed() -> None:
    add_ripple(py5.mouse_x, py5.mouse_y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ripple_field_####.png"))


py5.run_sketch()
