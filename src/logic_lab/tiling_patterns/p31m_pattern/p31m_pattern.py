from pathlib import Path
from math import pi, sqrt
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import add, from_angle, hex_lattice, mul, rotate, sub


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 3
scalar = 0.0
lattice = []
rand = []
line_color = None
curve_color = None


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
    global rand, line_color, curve_color
    rand = [py5.random(-1, 1) for _ in range(4)]
    line_color = py5.color(py5.random(1), 1, 1)
    curve_color = py5.color(py5.random(1), 1, 1)


def draw_line_pattern() -> None:
    vertices = []
    for i in range(2):
        point = from_angle(pi / 6, scalar / 3)
        point = add(point, mul((-scalar / sqrt(3), 0), abs(rand[i])))
        vertices.append(point)

    py5.fill(line_color)
    py5.begin_shape()
    py5.vertex(0, 0)
    py5.vertex(*vertices[0])
    py5.vertex(*vertices[1])
    py5.end_shape(py5.CLOSE)


def draw_curve_pattern() -> None:
    vertices = [from_angle(2 * pi * i / 3 + pi / 6, scalar / 6) for i in range(2)]
    controls = []
    for i in range(4):
        vec = sub(vertices[(i + 1) % 2], vertices[i % 2])
        controls.append(add(rotate(vec, rand[i] * pi / 3), vertices[i % 2]))

    py5.fill(curve_color)
    py5.begin_shape()
    py5.vertex(*vertices[0])
    py5.bezier_vertex(*controls[0], *controls[1], *vertices[1])
    py5.bezier_vertex(*controls[3], *controls[2], *vertices[0])
    py5.end_shape(py5.CLOSE)


def draw_triangle_motif() -> None:
    py5.push_matrix()
    offset = from_angle(-pi / 6, scalar / 3)
    py5.translate(*offset)
    for i in range(3):
        py5.push_matrix()
        py5.rotate(2 * pi * i / 3)
        draw_line_pattern()
        py5.pop_matrix()
    for i in range(3):
        py5.push_matrix()
        py5.rotate(2 * pi * i / 3)
        draw_curve_pattern()
        py5.pop_matrix()
    py5.pop_matrix()


def draw_tile() -> None:
    for mirror in (1, -1):
        for i in range(3):
            py5.push_matrix()
            py5.scale(1, mirror)
            py5.rotate(2 * pi * i / 3)
            draw_triangle_motif()
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
        py5.save_frame(str(SCREENSHOT_DIR / "p31m_pattern_####.png"))


py5.run_sketch()
