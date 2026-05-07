from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Preset:
    name: str
    seed: int
    rings: int
    base_step: float
    wobble: float
    eccentricity: float
    hue: float


PRESETS = [
    Preset("oak cross section", 17, 58, 5.2, 9.0, 0.12, 34),
    Preset("old cedar", 29, 92, 3.3, 5.5, 0.2, 22),
    Preset("burled wood", 43, 72, 4.3, 14.0, 0.34, 42),
]

preset_index = 0
show_growth_marks = True


def noisy_radius(angle: float, ring: int, preset: Preset) -> float:
    base = 18 + ring * preset.base_step
    slow = py5.noise(py5.cos(angle) * 0.85 + preset.seed, py5.sin(angle) * 0.85, ring * 0.035)
    fine = py5.noise(py5.cos(angle * 3.0) + ring * 0.04, py5.sin(angle * 3.0), preset.seed)
    season = 1.0 + 0.13 * py5.sin(ring * 0.72 + slow * py5.TWO_PI)
    return base * season + (slow - 0.5) * preset.wobble + (fine - 0.5) * preset.wobble * 0.38


def draw_ring(ring: int, preset: Preset) -> None:
    earlywood = ring % 2 == 0
    alpha = 20 if earlywood else 58
    brightness = 74 if earlywood else 48
    py5.stroke(preset.hue + py5.sin(ring * 0.19) * 8, 42, brightness, alpha)
    py5.stroke_weight(1.2 if earlywood else 2.1)
    py5.no_fill()
    py5.begin_shape()
    for i in range(130):
        angle = py5.TWO_PI * i / 129
        radius = noisy_radius(angle, ring, preset)
        x = py5.cos(angle) * radius * (1.0 + preset.eccentricity * 0.2)
        y = py5.sin(angle) * radius * (1.0 - preset.eccentricity)
        py5.curve_vertex(x, y)
    py5.end_shape(py5.CLOSE)


def draw_rays(preset: Preset) -> None:
    py5.stroke(preset.hue - 12, 28, 84, 18)
    py5.stroke_weight(0.8)
    for i in range(42):
        angle = py5.TWO_PI * i / 42 + py5.noise(i * 0.4, preset.seed) * 0.08
        inner = 16 + py5.noise(i, preset.seed) * 22
        outer = 18 + preset.rings * preset.base_step * py5.noise(i * 0.1, preset.seed + 20)
        py5.line(
            py5.cos(angle) * inner,
            py5.sin(angle) * inner,
            py5.cos(angle) * outer,
            py5.sin(angle) * outer,
        )


def draw_tree_rings() -> None:
    preset = PRESETS[preset_index]
    py5.noise_seed(preset.seed)
    py5.background(38, 13, 95)
    py5.translate(py5.width / 2, py5.height / 2)
    py5.rotate(py5.radians(-6))

    py5.no_stroke()
    py5.fill(preset.hue, 24, 86, 78)
    py5.circle(0, 0, preset.rings * preset.base_step * 2.35)

    if show_growth_marks:
        draw_rays(preset)
    for ring in range(preset.rings, 0, -1):
        draw_ring(ring, preset)

    py5.no_stroke()
    py5.fill(preset.hue + 4, 48, 50, 88)
    py5.circle(0, 0, 18)


def setup() -> None:
    py5.size(850, 850)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    draw_tree_rings()
    py5.no_loop()


def key_pressed() -> None:
    global preset_index, show_growth_marks
    if py5.key in {"1", "2", "3"}:
        preset_index = int(py5.key) - 1
        py5.redraw()
    elif py5.key == "m":
        show_growth_marks = not show_growth_marks
        py5.redraw()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "tree_ring_growth_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
