from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

line_count = 120
time_value = 0.0
animation_speed = 0.02


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += animation_speed

    for i in range(line_count):
        t = i / line_count
        angle1 = t * math.pi * 2

        x1 = 300 * math.cos(angle1)
        y1 = 300 * math.sin(angle1)

        offset = time_value + i * 0.15
        angle2 = angle1 + math.sin(offset) * math.pi / 3
        length = 150 + 80 * math.sin(offset)

        x2 = x1 + length * math.cos(angle2)
        y2 = y1 + length * math.sin(angle2)

        hue = (t * 360 + time_value * 50) % 360
        py5.stroke(hue, 70, 100)
        py5.stroke_weight(1.2)
        py5.line(x1, y1, x2, y2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "envelope_art_####.png"))


py5.run_sketch()
