from math import sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

itr = 0
SCALAR = 5


def setup() -> None:
    py5.size(500, 500)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global itr
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)

    py5.no_stroke()
    py5.fill(255, 0, 0, 127)
    draw_fermat_spiral(1.0 / 3)
    py5.fill(0, 0, 255, 127)
    draw_fermat_spiral(1.0 / 61)
    py5.fill(0, 255, 0, 127)
    draw_fermat_spiral(20.0 / 61)

    py5.pop_matrix()
    itr += 1


def draw_fermat_spiral(rot: float) -> None:
    theta = 2 * py5.PI * itr * rot
    x_pos = py5.cos(theta) * SCALAR * sqrt(itr)
    y_pos = py5.sin(theta) * SCALAR * sqrt(itr)
    py5.ellipse(x_pos, y_pos, SCALAR, SCALAR)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fermat_spiral_overlay_####.png"))


py5.run_sketch()

