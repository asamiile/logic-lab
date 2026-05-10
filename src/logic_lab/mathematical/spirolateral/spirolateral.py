from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
angle_step = 60
line_length = 8


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    x, y = 0, 0
    current_angle = 0
    total_iterations = int(60 + 40 * math.sin(time_value))

    py5.stroke_weight(2)
    py5.no_fill()

    for i in range(total_iterations):
        next_angle = current_angle + angle_step
        next_x = x + line_length * math.cos(math.radians(next_angle))
        next_y = y + line_length * math.sin(math.radians(next_angle))

        hue = (i / max(1, total_iterations) * 360 + time_value * 100) % 360
        py5.stroke(hue, 80, 100)

        py5.line(x, y, next_x, next_y)

        x, y = next_x, next_y
        current_angle = next_angle


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spirolateral_####.png"))


py5.run_sketch()
