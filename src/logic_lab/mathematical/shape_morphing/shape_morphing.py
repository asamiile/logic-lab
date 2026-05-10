from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
center_x = 500
center_y = 400
base_radius = 200


def generate_polygon_vertices(num_sides: int, radius: float) -> list[tuple[float, float]]:
    vertices = []
    for i in range(num_sides):
        angle = (2 * math.pi * i / num_sides) - (math.pi / 2)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)

    time_value += 0.02

    t = (math.sin(time_value) + 1) / 2

    triangle = generate_polygon_vertices(3, base_radius)
    hexagon = generate_polygon_vertices(6, base_radius)

    max_sides = max(len(triangle), len(hexagon))
    triangle_extended = triangle + triangle[: (max_sides - len(triangle))]
    hexagon_extended = hexagon + hexagon[: (max_sides - len(hexagon))]

    morphed = []
    for i in range(max_sides):
        x1, y1 = triangle_extended[i]
        x2, y2 = hexagon_extended[i]
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        morphed.append((x, y))

    py5.stroke_weight(2.5)
    py5.fill(240, 50, 80)
    py5.stroke(120 + t * 120, 80, 100)
    py5.begin_shape()
    for x, y in morphed:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)

    py5.no_fill()
    py5.stroke_weight(1)
    py5.stroke(0, 0, 60)
    py5.begin_shape()
    for x, y in triangle:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)

    py5.begin_shape()
    for x, y in hexagon:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "shape_morphing_####.png"))


py5.run_sketch()
