from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
line_spacing = 15


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    width = 500
    height = 400

    base_angle = time_value * 30
    phase_offset = math.sin(time_value) * 30

    num_lines_x = int(width * 2 / line_spacing) + 2
    num_lines_y = int(height * 2 / line_spacing) + 2

    py5.stroke_weight(1.2)

    angle1 = math.radians(base_angle)
    for i in range(num_lines_x):
        offset = (i * line_spacing) - width
        x1 = offset + height * math.tan(angle1)
        x2 = offset + height * math.tan(angle1) + 2 * width * math.cos(angle1)

        hue = (i / max(1, num_lines_x) * 180 + time_value * 50) % 360
        py5.stroke(hue, 70, 100)

        py5.line(x1, -height, x2, height)

    angle2 = math.radians(base_angle + phase_offset)
    for i in range(num_lines_y):
        offset = (i * line_spacing) - height
        y1 = offset + width * math.tan(angle2)
        y2 = offset + width * math.tan(angle2) + 2 * height * math.cos(angle2)

        hue = (180 + i / max(1, num_lines_y) * 180 + time_value * 50) % 360
        py5.stroke(hue, 70, 100)

        py5.line(-width, y1, width, y2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "line_interference_####.png"))


py5.run_sketch()
