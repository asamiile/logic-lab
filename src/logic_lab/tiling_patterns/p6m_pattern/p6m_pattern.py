import sys
from math import pi
from pathlib import Path

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import from_angle, hex_lattice, mul

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 5
scalar = 0.0
lattice = []
rand = []
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
    global rand, tile_color
    rand = [py5.random(-1, 1) for _ in range(4)]
    tile_color = py5.color(py5.random(1), 1, 1)


def draw_triangle() -> None:
    vertices = [from_angle(i * pi / 6, scalar) for i in range(2)]
    controls = [mul(vertices[i // 2], rand[i]) for i in range(4)]

    py5.fill(tile_color)
    py5.begin_shape()
    py5.vertex(0, 0)
    py5.vertex(*controls[0])
    py5.bezier_vertex(*controls[1], *controls[2], *controls[3])
    py5.end_shape(py5.CLOSE)


def draw_tile() -> None:
    for mirror in (1, -1):
        for i in range(6):
            py5.push_matrix()
            py5.scale(1, mirror)
            py5.rotate(2 * pi * i / 6)
            draw_triangle()
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
        py5.save_frame(str(SCREENSHOT_DIR / "p6m_pattern_####.png"))


py5.run_sketch()
