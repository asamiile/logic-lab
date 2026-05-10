from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
cols = 12
rows = 10
spacing = 50


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.015

    frequency = 0.05
    amplitude = 25

    grid: list[tuple[float, float]] = []
    for row in range(rows):
        for col in range(cols):
            base_x = (col - cols / 2) * spacing
            base_y = (row - rows / 2) * spacing

            offset_x = amplitude * math.sin(row * frequency + time_value)
            offset_y = amplitude * math.sin(col * frequency + time_value)

            x = base_x + offset_x
            y = base_y + offset_y

            grid.append((x, y))

    py5.no_fill()
    py5.stroke_weight(1.5)

    for row in range(rows):
        for col in range(cols - 1):
            idx1 = row * cols + col
            idx2 = row * cols + col + 1

            x1, y1 = grid[idx1]
            x2, y2 = grid[idx2]

            hue = (col / cols * 360 + time_value * 30) % 360
            py5.stroke(hue, 70, 100)
            py5.line(x1, y1, x2, y2)

    for col in range(cols):
        for row in range(rows - 1):
            idx1 = row * cols + col
            idx2 = (row + 1) * cols + col

            x1, y1 = grid[idx1]
            x2, y2 = grid[idx2]

            hue = (row / rows * 360 + 180 + time_value * 30) % 360
            py5.stroke(hue, 70, 100)
            py5.line(x1, y1, x2, y2)

    py5.fill(200, 50, 80)
    py5.no_stroke()
    for x, y in grid:
        py5.circle(x, y, 3)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "grid_deformation_####.png"))


py5.run_sketch()
