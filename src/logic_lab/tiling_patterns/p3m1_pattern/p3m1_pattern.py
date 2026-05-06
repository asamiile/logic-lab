from pathlib import Path
from math import pi, sqrt
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import add, from_angle, hex_lattice, sub


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 2
scalar = 0.0
lattice = []
gap = 0.18
tile_color = None


def setup() -> None:
    global scalar, lattice
    py5.size(500, 500, py5.P2D)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    lattice = hex_lattice(NUM, scalar, py5.height)
    make_pattern()
    draw_tiling()
    py5.no_loop()


def make_pattern() -> None:
    global gap, tile_color
    gap = py5.random(0.04, 0.35)
    tile_color = py5.color(py5.random(1), 0.75, 0.95, 0.65)


def next_triangle(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result = []
    for i, point in enumerate(vertices):
        direction = sub(vertices[(i + 1) % 3], point)
        result.append(add(point, (direction[0] * gap, direction[1] * gap)))
    return result


def draw_recursive_triangle() -> None:
    vertices = [
        from_angle(0, scalar / sqrt(3)),
        from_angle(pi / 3, scalar / sqrt(3)),
        (0.0, 0.0),
    ]

    py5.fill(tile_color)
    py5.stroke(0, 0, 0.2, 0.4)
    py5.stroke_weight(1)
    while py5.dist(*vertices[0], *vertices[1]) > 1:
        py5.begin_shape()
        for point in vertices:
            py5.vertex(*point)
        py5.end_shape(py5.CLOSE)
        vertices = next_triangle(vertices)


def draw_tile() -> None:
    for mirror in (1, -1):
        for i in range(3):
            py5.push_matrix()
            py5.scale(1, mirror)
            py5.rotate(2 * pi * i / 3)
            draw_recursive_triangle()
            py5.pop_matrix()


def draw_tiling() -> None:
    py5.background(0, 0, 1)
    for row in lattice:
        for x_val, y_val in row:
            py5.push_matrix()
            py5.translate(x_val, y_val)
            draw_tile()
            py5.pop_matrix()


def mouse_clicked() -> None:
    make_pattern()
    draw_tiling()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "p3m1_pattern_####.png"))


py5.run_sketch()
