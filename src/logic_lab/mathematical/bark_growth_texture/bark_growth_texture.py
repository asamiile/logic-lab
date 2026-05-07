from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Preset:
    name: str
    seed: int
    ridge_count: int
    crack_strength: float
    moss_amount: float
    hue: float


PRESETS = [
    Preset("old bark", 18, 78, 0.74, 0.22, 28),
    Preset("birch scars", 34, 54, 0.42, 0.08, 38),
    Preset("mossy trunk", 51, 88, 0.66, 0.48, 32),
]

preset_index = 0


def draw_bark() -> None:
    preset = PRESETS[preset_index]
    py5.noise_seed(preset.seed)
    py5.background(preset.hue, 22, 72)
    py5.no_stroke()

    stripe_width = py5.width / preset.ridge_count
    for i in range(preset.ridge_count):
        x = i * stripe_width
        phase = py5.noise(i * 0.16, preset.seed) * 80
        ridge = py5.noise(i * 0.09, preset.seed + 10)
        hue = preset.hue + py5.remap(ridge, 0, 1, -10, 12)
        brightness = py5.remap(ridge, 0, 1, 34, 78)
        py5.fill(hue, 42, brightness, 88)
        py5.begin_shape()
        py5.vertex(x, 0)
        for y in range(0, py5.height + 24, 24):
            drift = (py5.noise(i * 0.11, y * 0.012, preset.seed) - 0.5) * 22
            py5.vertex(x + stripe_width + drift + phase * 0.04, y)
        py5.vertex(x + stripe_width, py5.height)
        py5.vertex(x, py5.height)
        py5.end_shape(py5.CLOSE)

    for _ in range(420):
        x = py5.random(py5.width)
        y = py5.random(py5.height)
        grain = py5.noise(x * 0.018, y * 0.052, preset.seed)
        if grain < preset.crack_strength:
            py5.stroke(preset.hue - 10, 54, 18 + grain * 28, 38)
            py5.stroke_weight(py5.random(0.5, 2.8))
            length = py5.random(18, 90)
            bend = py5.random(-10, 10)
            py5.line(x, y, x + bend, y + length)

    py5.no_stroke()
    for _ in range(int(900 * preset.moss_amount)):
        x = py5.random(py5.width)
        y = py5.random(py5.height)
        moisture = py5.noise(x * 0.012, y * 0.012, preset.seed + 90)
        if moisture > 0.52:
            py5.fill(112 + py5.random(-22, 18), 44, py5.random(34, 68), py5.random(18, 42))
            py5.circle(x, y, py5.random(1.5, 6.5))

    py5.stroke(preset.hue - 14, 42, 24, 30)
    for y in range(20, py5.height, 34):
        if py5.noise(y * 0.03, preset.seed + 200) > 0.58:
            py5.stroke_weight(py5.random(0.7, 2.0))
            py5.line(
                py5.random(0, py5.width * 0.25),
                y,
                py5.random(py5.width * 0.75, py5.width),
                y + py5.random(-8, 8),
            )


def setup() -> None:
    py5.size(850, 850)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    draw_bark()
    py5.no_loop()


def key_pressed() -> None:
    global preset_index
    if py5.key in {"1", "2", "3"}:
        preset_index = int(py5.key) - 1
        py5.redraw()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "bark_growth_texture_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
