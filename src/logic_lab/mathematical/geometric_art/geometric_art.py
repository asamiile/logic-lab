from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0


def draw_triangle(x: float, y: float, size: float, rotation: float, depth: int) -> None:
    if depth <= 0:
        return

    angle = math.radians(rotation)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    h = size * math.sqrt(3) / 2

    vertices = [
        (x, y - h / 1.5),
        (x - size / 2, y + h / 3),
        (x + size / 2, y + h / 3),
    ]

    hue = (rotation * 2 + depth * 40) % 360
    py5.fill(hue, 70, 80)
    py5.stroke(hue, 80, 100)
    py5.stroke_weight(1)

    py5.begin_shape()
    for vx, vy in vertices:
        py5.vertex(vx, vy)
    py5.end_shape(py5.CLOSE)

    new_size = size * 0.6
    draw_triangle(x, y - h / 4, new_size, rotation + 30, depth - 1)
    draw_triangle(x - size / 4, y + h / 6, new_size, rotation - 30, depth - 1)
    draw_triangle(x + size / 4, y + h / 6, new_size, rotation + 90, depth - 1)


def draw_hexagon(x: float, y: float, size: float, rotation: float, depth: int) -> None:
    if depth <= 0:
        return

    vertices = []
    for i in range(6):
        angle = (2 * math.pi * i / 6) + math.radians(rotation)
        vx = x + size * math.cos(angle)
        vy = y + size * math.sin(angle)
        vertices.append((vx, vy))

    hue = (rotation * 3 + depth * 50) % 360
    py5.fill(hue, 60, 90)
    py5.stroke(hue, 80, 100)
    py5.stroke_weight(1.2)

    py5.begin_shape()
    for vx, vy in vertices:
        py5.vertex(vx, vy)
    py5.end_shape(py5.CLOSE)

    new_size = size * 0.5
    for i in range(6):
        angle = 2 * math.pi * i / 6
        cx = x + size * 0.7 * math.cos(angle)
        cy = y + size * 0.7 * math.sin(angle)
        draw_hexagon(cx, cy, new_size, rotation + 20, depth - 1)


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)

    time_value += 0.015

    blend = (math.sin(time_value) + 1) / 2

    triangle_depth = int(3 + blend * 2)
    triangle_rotation = time_value * 30

    py5.push_matrix()
    py5.translate(250, 400)
    draw_triangle(0, 0, 150, triangle_rotation, triangle_depth)
    py5.pop_matrix()

    hexagon_depth = int(2 + blend * 1.5)
    hexagon_rotation = -time_value * 25

    py5.push_matrix()
    py5.translate(750, 400)
    draw_hexagon(0, 0, 100, hexagon_rotation, hexagon_depth)
    py5.pop_matrix()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "geometric_art_####.png"))


py5.run_sketch()
