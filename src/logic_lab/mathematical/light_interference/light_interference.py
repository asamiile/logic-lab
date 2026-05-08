from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 3
phase = 0.0
source_count = 2
threshold = False


def setup() -> None:
    py5.size(780, 680)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase
    phase += 0.035
    field = compute_field()
    draw_field(field)
    draw_sources()


def source_positions() -> list[tuple[float, float]]:
    cx, cy = py5.width * 0.5, py5.height * 0.38
    spacing = 64
    return [(cx + (i - (source_count - 1) * 0.5) * spacing, cy) for i in range(source_count)]


def compute_field() -> np.ndarray:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    values = np.zeros((rows, cols), dtype=np.float32)
    sources = source_positions()
    wavelength = 34.0
    for row in range(rows):
        y = row * PIXEL_STEP
        for col in range(cols):
            x = col * PIXEL_STEP
            amplitude = 0.0
            for sx, sy in sources:
                distance = math.hypot(x - sx, y - sy)
                amplitude += math.cos(py5.TWO_PI * distance / wavelength - phase) / (
                    1 + distance * 0.004
                )
            values[row, col] = amplitude / len(sources)
    return values


def draw_field(values: np.ndarray) -> None:
    py5.no_stroke()
    rows, cols = values.shape
    for row in range(rows):
        for col in range(cols):
            v = float(values[row, col])
            if threshold:
                bright = 96 if v > 0.18 else 12 if v < -0.18 else 42
                py5.fill(214, 58, bright, 100)
            else:
                hue = (214 + v * 92) % 360
                py5.fill(hue, 68, 42 + abs(v) * 54, 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def draw_sources() -> None:
    py5.no_stroke()
    for sx, sy in source_positions():
        py5.fill(48, 88, 100, 92)
        py5.circle(sx, sy, 16)
        py5.fill(48, 88, 100, 18)
        py5.circle(sx, sy, 52)


def key_pressed() -> None:
    global source_count, threshold
    if py5.key in {"2", "3", "4", "5"}:
        source_count = int(py5.key)
    elif py5.key == "t":
        threshold = not threshold
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "light_interference_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
