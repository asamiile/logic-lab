from math import sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

itr = 0
SCALAR = 30


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.background(255)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke(0, 0, 255)
    draw_line(10)
    py5.stroke(255, 0, 0)
    draw_real_curve(1.0 / 10)
    py5.pop_matrix()


def draw() -> None:
    global itr
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.no_stroke()
    draw_fermat_spiral(1.0 / 10)
    py5.pop_matrix()
    itr += 1


def draw_fermat_spiral(rot: float) -> None:
    theta = 2 * py5.PI * itr * rot
    x_pos = py5.cos(theta) * SCALAR * sqrt(itr)
    y_pos = py5.sin(theta) * SCALAR * sqrt(itr)
    py5.fill(0)
    py5.ellipse(x_pos, y_pos, 10, 10)


def draw_line(n: int) -> None:
    for i in range(n // 2 + 1):
        theta = 2 * i * py5.PI / n
        x_pos = py5.cos(theta) * py5.width / sqrt(2)
        y_pos = py5.sin(theta) * py5.width / sqrt(2)
        py5.line(x_pos, y_pos, -x_pos, -y_pos)


def draw_real_curve(rot: float) -> None:
    step = 2 * py5.PI * 0.01
    theta = 0.0
    rad = 0.0

    py5.no_fill()
    py5.begin_shape()
    while rad < py5.width / sqrt(2):
        rad = SCALAR * sqrt(theta / (2 * py5.PI * rot))
        x_pos = py5.cos(theta) * rad
        y_pos = py5.sin(theta) * rad
        py5.vertex(x_pos, y_pos)
        theta += step
    py5.end_shape()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fermat_spiral_line_####.png"))


py5.run_sketch()

