from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

point_count = 180
jump_multiplier = 2.0
radius = 250.0
rotation_speed = 0.01

rotation_offset = 0.0


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global rotation_offset

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    rotation_offset += rotation_speed

    vertices = []
    for i in range(point_count):
        angle = (2 * math.pi * i / point_count) + rotation_offset
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        vertices.append((x, y))

    hue_offset = (rotation_offset * 180 / math.pi) % 360
    py5.stroke_weight(1.5)
    py5.no_fill()

    for i in range(point_count):
        start_idx = i
        end_idx = int((i * jump_multiplier) % point_count)

        x1, y1 = vertices[start_idx]
        x2, y2 = vertices[end_idx]

        hue = (hue_offset + (i / point_count * 360)) % 360
        py5.stroke(hue, 80, 100)

        py5.line(x1, y1, x2, y2)

    py5.no_stroke()
    py5.fill(200, 10, 100)
    for x, y in vertices:
        py5.circle(x, y, 3)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "string_art_####.png"))


py5.run_sketch()
