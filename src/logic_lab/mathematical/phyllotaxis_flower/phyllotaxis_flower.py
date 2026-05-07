from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
GOLDEN_ANGLE = py5.radians(137.507764)


@dataclass(frozen=True)
class Preset:
    name: str
    count: int
    scale: float
    petal_scale: float
    hue_start: float
    hue_shift: float
    rotate_petals: bool


PRESETS = [
    Preset("sunflower seeds", 720, 7.1, 0.82, 38, 72, True),
    Preset("daisy florets", 420, 8.4, 1.25, 54, 118, True),
    Preset("succulent rosette", 360, 9.0, 1.65, 126, 54, False),
]

preset_index = 0


def draw_seed(x: float, y: float, radius: float, angle: float, hue: float, preset: Preset) -> None:
    py5.push_matrix()
    py5.translate(x, y)
    py5.rotate(angle if preset.rotate_petals else angle * 0.18)
    py5.no_stroke()
    py5.fill(hue, 58, 86, 88)
    py5.ellipse(0, 0, radius * preset.petal_scale, radius * 0.74)
    py5.fill(hue + 18, 42, 98, 36)
    py5.ellipse(-radius * 0.12, -radius * 0.12, radius * 0.42, radius * 0.22)
    py5.pop_matrix()


def draw_flower() -> None:
    preset = PRESETS[preset_index]
    py5.background(45, 12, 96)
    py5.translate(py5.width / 2, py5.height / 2)

    for i in range(preset.count, 0, -1):
        angle = i * GOLDEN_ANGLE
        radius = preset.scale * py5.sqrt(i)
        x = py5.cos(angle) * radius
        y = py5.sin(angle) * radius
        distance_ratio = i / preset.count
        seed_size = py5.remap(distance_ratio, 0, 1, 14, 4.5)
        hue = preset.hue_start + py5.sin(i * 0.037) * preset.hue_shift
        draw_seed(x, y, seed_size, angle, hue, preset)

    py5.no_stroke()
    py5.fill(42, 76, 86, 92)
    py5.circle(0, 0, 16)


def setup() -> None:
    py5.size(800, 800)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    draw_flower()
    py5.no_loop()


def key_pressed() -> None:
    global preset_index
    if py5.key in {"1", "2", "3"}:
        preset_index = int(py5.key) - 1
        py5.redraw()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "phyllotaxis_flower_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
