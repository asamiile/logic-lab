from math import ceil, sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 10
scalar = 0.0
lattice: list[list[tuple[float, float]]] = []
base0 = (0.0, 1.0)
base1 = (0.0, 0.0)


def setup() -> None:
    global scalar, base1
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    base1 = (py5.cos(py5.PI / 6), py5.sin(py5.PI / 6))
    make_lattice()
    draw_tiling()
    py5.no_loop()


def make_lattice() -> None:
    global lattice
    cols = ceil(NUM / base1[0])
    lattice = []
    for i in range(NUM + 1):
        row = []
        for j in range(cols + 1):
            x_pos = (base0[0] * i + base1[0] * j) * scalar
            y_pos = ((base0[1] * i + base1[1] * j) * scalar) % (py5.height + scalar)
            row.append((x_pos, y_pos))
        lattice.append(row)


def draw_tiling() -> None:
    py5.background(0, 0, 1)
    for row in lattice:
        for x_pos, y_pos in row:
            py5.fill(py5.random(1), 1, 1)
            draw_hex_tile(x_pos, y_pos)


def draw_hex_tile(x_pos: float, y_pos: float) -> None:
    radius = scalar / sqrt(3)
    py5.begin_shape()
    for i in range(6):
        angle = py5.TWO_PI * i / 6
        py5.vertex(x_pos + py5.cos(angle) * radius, y_pos + py5.sin(angle) * radius)
    py5.end_shape(py5.CLOSE)


def mouse_clicked() -> None:
    draw_tiling()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hex_tiling_####.png"))


py5.run_sketch()

