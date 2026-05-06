from pathlib import Path
from math import pi
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import add, from_angle, hex_lattice, rotate, sub


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 5
scalar = 0.0
lattice = []
rand = []


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
    global rand
    rand = [py5.random(-1, 1) for _ in range(4)]


def draw_triangle_curve() -> None:
    vertices = [(0.0, 0.0), from_angle(pi / 6, scalar / 2)]
    controls = []
    for i in range(2):
        vec = sub(vertices[(i + 1) % 2], vertices[i])
        controls.append(add(rotate(vec, rand[i] * pi / 3), vertices[i]))

    py5.no_fill()
    py5.stroke(0)
    py5.stroke_weight(3)
    py5.begin_shape()
    py5.vertex(*vertices[0])
    py5.bezier_vertex(*controls[0], *controls[1], *vertices[1])
    py5.end_shape()


def draw_tile() -> None:
    for i in range(6):
        py5.push_matrix()
        py5.rotate(2 * pi * i / 6)
        draw_triangle_curve()
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
        py5.save_frame(str(SCREENSHOT_DIR / "p6_pattern_####.png"))


py5.run_sketch()
