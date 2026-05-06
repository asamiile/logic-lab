from math import sqrt
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 10
scalar = 0.0
lattice: list[list[tuple[float, float]]] = []


def setup() -> None:
    global scalar
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    make_lattice()
    draw_tiling()
    py5.no_loop()


def make_lattice() -> None:
    global lattice
    lattice = [[(j * scalar, i * scalar) for j in range(NUM + 1)] for i in range(NUM + 1)]


def draw_tiling() -> None:
    py5.background(0, 0, 1)
    for row in lattice:
        for x_pos, y_pos in row:
            py5.fill(py5.random(1), 1, 1)
            draw_square_tile(x_pos, y_pos)


def draw_square_tile(x_pos: float, y_pos: float) -> None:
    py5.begin_shape()
    for i in range(4):
        angle = py5.TWO_PI * (i + 0.5) / 4
        radius = scalar / sqrt(2)
        py5.vertex(x_pos + py5.cos(angle) * radius, y_pos + py5.sin(angle) * radius)
    py5.end_shape(py5.CLOSE)


def mouse_clicked() -> None:
    draw_tiling()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "square_tiling_####.png"))


py5.run_sketch()
