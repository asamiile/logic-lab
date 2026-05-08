from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 4
phase = 0.0
show_rays = False


def setup() -> None:
    py5.size(880, 640)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase
    phase += 0.025
    density = compute_density()
    draw_density(density)
    if show_rays:
        draw_sample_rays()


def compute_density() -> np.ndarray:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    density = np.zeros((rows, cols), dtype=np.float32)
    for x in range(8, py5.width - 8, 5):
        surface_y = py5.height * 0.28 + wave_height(x)
        slope = wave_slope(x)
        bend = -slope * 1.45
        target_x = x + bend * 250
        for depth in range(1, 5):
            y = surface_y + depth * 92
            cx = int((target_x + math.sin(depth + phase) * 7) / PIXEL_STEP)
            cy = int(y / PIXEL_STEP)
            if 0 <= cx < cols and 0 <= cy < rows:
                density[cy, cx] += 1.0 / depth
    for _ in range(3):
        density = blur(density)
    return density


def wave_height(x: float) -> float:
    return math.sin(x * 0.018 + phase) * 18 + math.sin(x * 0.041 - phase * 1.4) * 7


def wave_slope(x: float) -> float:
    return math.cos(x * 0.018 + phase) * 0.018 * 18 + math.cos(x * 0.041 - phase * 1.4) * 0.041 * 7


def blur(values: np.ndarray) -> np.ndarray:
    padded = np.pad(values, 1, mode="edge")
    return (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        + padded[1:-1, 1:-1] * 3
    ) / 7.0


def draw_density(density: np.ndarray) -> None:
    py5.background(207, 54, 16)
    py5.no_stroke()
    rows, cols = density.shape
    maximum = max(float(density.max()), 0.001)
    for row in range(rows):
        for col in range(cols):
            v = min(1.0, float(density[row, col]) / maximum)
            hue = 188 + v * 34
            py5.fill(hue, 64 - v * 30, 20 + v * 78, 32 + v * 68)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)
    draw_water_surface()


def draw_water_surface() -> None:
    py5.no_fill()
    py5.stroke(184, 28, 96, 74)
    py5.stroke_weight(2)
    py5.begin_shape()
    for x in range(0, py5.width + 8, 8):
        py5.vertex(x, py5.height * 0.28 + wave_height(x))
    py5.end_shape()


def draw_sample_rays() -> None:
    py5.stroke(48, 40, 100, 18)
    py5.stroke_weight(1)
    for x in range(30, py5.width, 35):
        y = py5.height * 0.28 + wave_height(x)
        target_x = x - wave_slope(x) * 360
        py5.line(x, 0, x, y)
        py5.line(x, y, target_x, py5.height)


def key_pressed() -> None:
    global show_rays
    if py5.key == "v":
        show_rays = not show_rays
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "caustic_light_field_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
