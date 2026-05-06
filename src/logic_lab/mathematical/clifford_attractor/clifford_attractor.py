from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    ("classic", -1.4, 1.6, 1.0, 0.7),
    ("nebula", -1.8, -2.0, -0.5, -0.9),
    ("orchid", 1.7, 1.7, 0.6, 1.2),
    ("butterfly", -1.7, 1.8, -1.9, -0.4),
    ("filament", 1.5, -1.8, 1.6, 0.9),
]

preset_index = 0
point_count = 420_000
color_mode_index = 0
needs_render = True
density: np.ndarray | None = None


def setup() -> None:
    py5.size(760, 760)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global needs_render, density

    if needs_render:
        density = compute_density()
        needs_render = False
    if density is not None:
        draw_density(density)
    draw_info()
    py5.no_loop()


def compute_density() -> np.ndarray:
    name, a, b, c, d = PRESETS[preset_index]
    _ = name
    values = np.zeros((py5.height, py5.width), dtype=np.float32)

    x = 0.1
    y = 0.0
    warmup = 1_000
    bounds = estimate_bounds(a, b, c, d)
    min_x, max_x, min_y, max_y = bounds

    for i in range(point_count + warmup):
        x, y = next_point(x, y, a, b, c, d)
        if i < warmup:
            continue

        px = int((x - min_x) / (max_x - min_x) * (py5.width - 1))
        py = int((y - min_y) / (max_y - min_y) * (py5.height - 1))
        if 0 <= px < py5.width and 0 <= py < py5.height:
            values[py, px] += 1

    return np.log1p(values)


def estimate_bounds(a: float, b: float, c: float, d: float) -> tuple[float, float, float, float]:
    x = 0.1
    y = 0.0
    xs = []
    ys = []
    for i in range(50_000):
        x, y = next_point(x, y, a, b, c, d)
        if i > 500:
            xs.append(x)
            ys.append(y)

    pad_x = (max(xs) - min(xs)) * 0.08
    pad_y = (max(ys) - min(ys)) * 0.08
    return min(xs) - pad_x, max(xs) + pad_x, min(ys) - pad_y, max(ys) + pad_y


def next_point(x: float, y: float, a: float, b: float, c: float, d: float) -> tuple[float, float]:
    return math.sin(a * y) + c * math.cos(a * x), math.sin(b * x) + d * math.cos(b * y)


def draw_density(values: np.ndarray) -> None:
    max_value = float(values.max())
    py5.no_stroke()
    for y in range(py5.height):
        for x in range(py5.width):
            v = float(values[y, x]) / max(1e-6, max_value)
            if v <= 0:
                py5.fill(224, 18, 6, 100)
            else:
                hue = hue_for_value(v, x, y)
                py5.fill(hue, 74, min(100, 14 + v * 112), 100)
            py5.rect(x, y, 1, 1)


def hue_for_value(value: float, x: int, y: int) -> float:
    if color_mode_index == 1:
        angle = math.atan2(y - py5.height * 0.5, x - py5.width * 0.5)
        return (math.degrees(angle) + 360) % 360
    if color_mode_index == 2:
        radius = math.hypot(x - py5.width * 0.5, y - py5.height * 0.5)
        return (190 + radius * 0.12 + value * 120) % 360
    return 190 + value * 92


def draw_info() -> None:
    name, a, b, c, d = PRESETS[preset_index]
    py5.no_stroke()
    py5.fill(224, 24, 12, 90)
    py5.rect(14, 14, 620, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Clifford attractor | {name} a={a:.1f} b={b:.1f} c={c:.1f} d={d:.1f} | n: preset | +/-: points {point_count // 1000}k | c: color | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, point_count, color_mode_index, needs_render

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "clifford_attractor_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        needs_render = True
        py5.loop()
    elif py5.key == "+":
        point_count = min(1_200_000, point_count + 80_000)
        needs_render = True
        py5.loop()
    elif py5.key == "-":
        point_count = max(80_000, point_count - 80_000)
        needs_render = True
        py5.loop()
    elif py5.key == "c":
        color_mode_index = (color_mode_index + 1) % 3
        needs_render = True
        py5.loop()


py5.run_sketch()
