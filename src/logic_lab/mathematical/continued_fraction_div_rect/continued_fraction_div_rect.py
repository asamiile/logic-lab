from math import sqrt
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
RATIO = sqrt(2)


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.background(0, 0, 1)
    div_rect(0, 0, py5.width)
    py5.no_loop()


def div_rect(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = x_pos + wd
    y_end_pos = y_pos + wd / RATIO

    while wd > 0.1:
        itr += 1
        py5.fill(py5.random(1), 1, 1)
        if itr % 2 == 0:
            while x_pos + wd < x_end_pos + 0.1:
                py5.rect(x_pos, y_pos, wd, wd)
                x_pos += wd
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd < y_end_pos + 0.1:
                py5.rect(x_pos, y_pos, wd, wd)
                y_pos += wd
            wd = y_end_pos - y_pos


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "continued_fraction_div_rect_####.png"))


py5.run_sketch()
