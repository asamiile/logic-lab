from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Preset:
    name: str
    petals: int
    layers: int
    base_radius: float
    petal_length: float
    petal_width: float
    notch: float
    twist: float
    hue: float


PRESETS = [
    Preset("camellia", 9, 4, 38, 178, 54, 0.08, 0.08, 338),
    Preset("dahlia", 15, 5, 30, 150, 34, 0.18, 0.23, 26),
    Preset("water lily", 12, 3, 44, 190, 42, 0.05, -0.16, 304),
]

preset_index = 0
time_offset = 0.0


def petal_radius(theta: float, preset: Preset) -> float:
    tip = py5.sin(theta) ** 0.58
    shoulder = 1.0 + 0.16 * py5.sin(theta * 3)
    notch = 1.0 - preset.notch * py5.exp(-((theta - py5.HALF_PI) ** 2) / 0.06)
    return preset.petal_width * tip * shoulder * notch


def draw_petal(length: float, width: float, hue: float, preset: Preset) -> None:
    py5.begin_shape()
    for i in range(34):
        t = i / 33
        theta = py5.PI * t
        y = -length * t
        x = petal_radius(theta, preset) * width
        py5.curve_vertex(x, y)
    for i in range(33, -1, -1):
        t = i / 33
        theta = py5.PI * t
        y = -length * t
        x = -petal_radius(theta, preset) * width
        py5.curve_vertex(x, y)
    py5.end_shape(py5.CLOSE)

    py5.stroke(hue + 8, 28, 96, 26)
    py5.stroke_weight(0.8)
    for k in (-0.34, 0, 0.34):
        py5.line(0, 0, k * preset.petal_width, -length * 0.78)


def draw_flower() -> None:
    preset = PRESETS[preset_index]
    py5.background(42, 10, 96)
    py5.translate(py5.width / 2, py5.height / 2)
    py5.rotate(time_offset * 0.15)

    for layer in range(preset.layers, 0, -1):
        layer_ratio = layer / preset.layers
        count = preset.petals + (preset.layers - layer) * 2
        radius = preset.base_radius * layer_ratio
        length = preset.petal_length * (0.72 + layer_ratio * 0.28)
        width = 0.68 + layer_ratio * 0.42
        phase = layer * preset.twist + time_offset * (0.04 + layer * 0.006)

        for i in range(count):
            angle = py5.TWO_PI * i / count + phase
            py5.push_matrix()
            py5.rotate(angle)
            py5.translate(0, -radius)
            py5.rotate(py5.sin(time_offset + i * 0.7 + layer) * 0.035)
            hue = preset.hue + layer * 5 + py5.sin(i * 0.8) * 6
            py5.no_stroke()
            py5.fill(hue, 46 + layer * 5, 86 - layer * 3, 54 + layer * 8)
            draw_petal(length, width, hue, preset)
            py5.pop_matrix()

    py5.no_stroke()
    py5.fill(43, 78, 90, 92)
    py5.circle(0, 0, preset.base_radius * 1.05)
    py5.fill(34, 62, 78, 80)
    for i in range(24):
        angle = py5.TWO_PI * i / 24
        py5.circle(py5.cos(angle) * 13, py5.sin(angle) * 13, 4.5)


def setup() -> None:
    py5.size(850, 850)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_offset
    draw_flower()
    time_offset += 0.018


def key_pressed() -> None:
    global preset_index, time_offset
    if py5.key in {"1", "2", "3"}:
        preset_index = int(py5.key) - 1
        time_offset = 0.0
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "petal_morphogenesis_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
