from __future__ import annotations

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

RANGES = [
    ("full", 2.5, 4.0),
    ("chaos edge", 3.35, 3.72),
    ("deep chaos", 3.72, 4.0),
    ("period window", 3.80, 3.88),
]

range_index = 0
iteration_count = 900
settle_count = 260
color_mode_index = 0
needs_render = True
density: np.ndarray | None = None


def setup() -> None:
    py5.size(820, 560)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global needs_render, density

    if needs_render:
        density = compute_density()
        needs_render = False
    py5.background(220, 14, 96)
    if density is not None:
        draw_density(density)
    draw_axes()
    draw_info()
    py5.no_loop()


def compute_density() -> np.ndarray:
    _, r_min, r_max = RANGES[range_index]
    values = np.zeros((py5.height, py5.width), dtype=np.float32)

    for col in range(py5.width):
        r = r_min + (r_max - r_min) * col / max(1, py5.width - 1)
        x = 0.5
        for i in range(iteration_count):
            x = r * x * (1 - x)
            if i < settle_count:
                continue
            row = py5.height - 1 - int(x * (py5.height - 1))
            if 0 <= row < py5.height:
                values[row, col] += 1

    return np.log1p(values)


def draw_density(values: np.ndarray) -> None:
    max_value = float(values.max())
    py5.no_stroke()
    for y in range(py5.height):
        for x in range(py5.width):
            v = float(values[y, x]) / max(1e-6, max_value)
            if v <= 0:
                py5.fill(220, 15, 96, 100)
            else:
                hue = hue_for_density(v, x, y)
                py5.fill(hue, 72, min(100, 18 + v * 110), 100)
            py5.rect(x, y, 1, 1)


def hue_for_density(value: float, x: int, y: int) -> float:
    if color_mode_index == 1:
        return (190 + x * 90 / max(1, py5.width)) % 360
    if color_mode_index == 2:
        return (32 + y * 140 / max(1, py5.height)) % 360
    return 205 + value * 92


def draw_axes() -> None:
    _, r_min, r_max = RANGES[range_index]
    py5.stroke(220, 22, 20, 48)
    py5.stroke_weight(1)
    for i in range(6):
        x = i * (py5.width - 1) / 5
        py5.line(x, 0, x, py5.height)
        r = r_min + (r_max - r_min) * i / 5
        py5.no_stroke()
        py5.fill(220, 28, 18, 86)
        py5.text(f"{r:.2f}", x + 4, py5.height - 12)
        py5.stroke(220, 22, 20, 48)

    for i in range(5):
        y = i * (py5.height - 1) / 4
        py5.line(0, y, py5.width, y)


def draw_info() -> None:
    name, r_min, r_max = RANGES[range_index]
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 640, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Logistic bifurcation | {name} r=[{r_min:.2f}, {r_max:.2f}] | iterations {iteration_count} | n: range | +/-: iterations | c: color | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global range_index, iteration_count, color_mode_index, needs_render

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "logistic_bifurcation_####.png"))
    elif py5.key == "n":
        range_index = (range_index + 1) % len(RANGES)
        needs_render = True
        py5.loop()
    elif py5.key == "+":
        iteration_count = min(1800, iteration_count + 120)
        needs_render = True
        py5.loop()
    elif py5.key == "-":
        iteration_count = max(360, iteration_count - 120)
        needs_render = True
        py5.loop()
    elif py5.key == "c":
        color_mode_index = (color_mode_index + 1) % 3
        needs_render = True
        py5.loop()


py5.run_sketch()
