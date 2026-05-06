import sys
from math import pi, sqrt
from pathlib import Path

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import add, from_angle, square_lattice, sub

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 5
scalar = 0.0
lattice = []
gap = 0.0
tile_color = None
background_color = None


def setup() -> None:
    global scalar, lattice
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    lattice = square_lattice(NUM, scalar)
    make_square_triangle()
    draw_tiling()
    py5.no_loop()


def make_square_triangle() -> None:
    global gap, tile_color, background_color
    gap = py5.random(1)
    tile_color = py5.color(py5.random(1), 0.4, 1)
    background_color = py5.color(py5.random(1), 1, 1)


def shifted_vertices(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result = []
    for i, point in enumerate(vertices):
        direction = sub(vertices[(i + 1) % 4], point)
        result.append(add(point, (direction[0] * gap, direction[1] * gap)))
    return result


def draw_triangle_quarter() -> None:
    vertices = [from_angle(pi * (i + 0.5) / 2, 0.5 * scalar / sqrt(2)) for i in range(4)]
    inner = shifted_vertices(vertices)
    py5.fill(tile_color)
    for i in range(4):
        py5.begin_shape()
        py5.vertex(*vertices[i])
        py5.vertex(*inner[i])
        py5.vertex(*inner[(i + 3) % 4])
        py5.end_shape(py5.CLOSE)


def draw_tile() -> None:
    for sx in (1, -1):
        for sy in (1, -1):
            py5.push_matrix()
            py5.scale(sx, sy)
            py5.translate(scalar / 4, scalar / 4)
            draw_triangle_quarter()
            py5.pop_matrix()


def draw_tiling() -> None:
    py5.background(background_color)
    for row in lattice:
        for x_val, y_val in row:
            py5.push_matrix()
            py5.translate(x_val, y_val)
            draw_tile()
            py5.pop_matrix()


def mouse_clicked() -> None:
    make_square_triangle()
    draw_tiling()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "square_triangle_periodic_####.png"))


py5.run_sketch()
