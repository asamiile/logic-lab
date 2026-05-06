from math import sqrt
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

RATIO = (sqrt(5) + 1) / 2
thr = 80.0
thr2 = 0.5


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_current()
    py5.no_loop()


def draw_current() -> None:
    py5.background(0, 0, 1)
    color_rect(0, 0, py5.width, py5.width)
    div_square(0, 0, py5.width)


def color_rect(x_pos: float, y_pos: float, wd: float, ht: float) -> None:
    val = py5.random(1)
    if val < 0.15:
        py5.fill(0, 1, 1)
    elif val < 0.3:
        py5.fill(2.0 / 3, 1, 1)
    elif val < 0.45:
        py5.fill(1.0 / 6, 1, 1)
    elif val < 0.5:
        py5.fill(0, 1, 0)
    elif val < 0.7:
        py5.fill(0, 0, 0.9)
    else:
        py5.fill(0, 0, 1)
    py5.stroke_weight(5)
    py5.rect(x_pos, y_pos, wd, ht)


def div_rect(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = x_pos + wd
    y_end_pos = y_pos + wd / RATIO

    while wd > thr:
        itr += 1
        if itr % 2 == 0:
            while x_pos + wd < x_end_pos + 0.1:
                color_rect(x_pos, y_pos, wd, wd)
                if py5.random(1) < thr2:
                    div_square(x_pos, y_pos, wd)
                x_pos += wd
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd < y_end_pos + 0.1:
                color_rect(x_pos, y_pos, wd, wd)
                if py5.random(1) < thr2:
                    div_square(x_pos, y_pos, wd)
                y_pos += wd
            wd = y_end_pos - y_pos


def div_square(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = wd + x_pos
    y_end_pos = wd + y_pos

    while wd > thr:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd * RATIO < x_end_pos + 0.1:
                color_rect(x_pos, y_pos, wd * RATIO, wd)
                if py5.random(1) < thr2:
                    div_rect(x_pos, y_pos, wd * RATIO)
                x_pos += wd * RATIO
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd / RATIO < y_end_pos + 0.1:
                color_rect(x_pos, y_pos, wd, wd / RATIO)
                if py5.random(1) < thr2:
                    div_rect(x_pos, y_pos, wd)
                y_pos += wd / RATIO
            wd = y_end_pos - y_pos


def mouse_clicked() -> None:
    global thr, thr2
    thr = int(py5.random(10, 300))
    thr2 = py5.random(0, 1)
    print("thr =", thr, "thr2 =", thr2)
    draw_current()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "continued_fraction_mondrian_####.png"))


py5.run_sketch()
