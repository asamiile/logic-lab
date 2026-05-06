from math import sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

M = 1
NUM = 10


def setup() -> None:
    py5.size(500, 200)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_convergent()
    py5.no_loop()


def draw_convergent() -> None:
    x = float(M)
    alpha = (M + sqrt(M * M + 4)) / 2
    lim_pos = py5.remap(alpha, M, M + 1, 0, py5.height)
    step = py5.width / NUM

    py5.background(255)
    py5.stroke(255, 0, 0)
    py5.line(0, lim_pos, py5.width, lim_pos)
    py5.stroke(0)

    for i in range(NUM):
        next_x = M + 1.0 / x
        pos = py5.remap(x, M, M + 1, 0, py5.height)
        next_pos = py5.remap(next_x, M, M + 1, 0, py5.height)
        py5.line(i * step, pos, (i + 1) * step, next_pos)
        x = next_x


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fibonacci_convergent_####.png"))


py5.run_sketch()

