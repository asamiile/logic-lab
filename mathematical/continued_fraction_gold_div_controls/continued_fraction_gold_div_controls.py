from datetime import datetime
from math import sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

ratio = (1 + sqrt(5)) / 2
thr = 100.0
thr2 = 0.5
mond = False
rand1: list[float] = []
rand2: list[float] = []
count = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.no_loop()
    py5.redraw()


def draw() -> None:
    global count
    py5.background(1, 0, 1)
    count = 0
    col_rect(0, 0, py5.width, py5.width)
    div_square(0, 0, py5.width)
    draw_status()


def draw_status() -> None:
    py5.no_stroke()
    py5.fill(0)
    py5.rect(0, 0, 230, 72)
    py5.fill(0, 0, 1)
    py5.text_size(12)
    py5.text(f"thr {int(thr)}  thr2 {thr2:.2f}  mond {mond}", 10, 20)
    py5.text("A/Z thr  S/X thr2  M mode", 10, 40)
    py5.text("R colors  P save", 10, 60)
    py5.stroke(0)


def col_rect(x_pos: float, y_pos: float, wd: float, ht: float) -> None:
    global count
    if len(rand1) <= count:
        rand1.append(py5.random(1))
        rand2.append(py5.random(1))

    if mond:
        mondrian_color(rand2[count])
    else:
        py5.fill(rand2[count], 1, 1)
        py5.stroke_weight(1)

    py5.rect(x_pos, y_pos, wd, ht)
    count += 1


def change_color() -> None:
    for i in range(len(rand1)):
        rand1[i] = py5.random(1)
        rand2[i] = py5.random(1)


def mondrian_color(val: float) -> None:
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


def div_rect(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = x_pos + wd
    y_end_pos = y_pos + wd / ratio

    while wd > thr:
        itr += 1
        if itr % 2 == 0:
            while x_pos + wd < x_end_pos + 0.1:
                col_rect(x_pos, y_pos, wd, wd)
                if rand1[count - 1] > thr2:
                    div_square(x_pos, y_pos, wd)
                x_pos += wd
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd < y_end_pos + 0.1:
                col_rect(x_pos, y_pos, wd, wd)
                if rand1[count - 1] > thr2:
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
            while x_pos + wd * ratio < x_end_pos + 0.1:
                col_rect(x_pos, y_pos, wd * ratio, wd)
                if rand1[count - 1] > thr2:
                    div_rect(x_pos, y_pos, wd * ratio)
                x_pos += wd * ratio
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd / ratio < y_end_pos + 0.1:
                col_rect(x_pos, y_pos, wd, wd / ratio)
                if rand1[count - 1] > thr2:
                    div_rect(x_pos, y_pos, wd)
                y_pos += wd / ratio
            wd = y_end_pos - y_pos


def key_pressed() -> None:
    global thr, thr2, mond

    key = str(py5.key).lower()
    if key == "a":
        thr = min(300, thr + 10)
    elif key == "z":
        thr = max(10, thr - 10)
    elif key == "s":
        thr2 = min(1, thr2 + 0.05)
    elif key == "x":
        thr2 = max(0, thr2 - 0.05)
    elif key == "m":
        mond = not mond
    elif key == "r":
        change_color()
    elif key == "p":
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        py5.save_frame(str(SCREENSHOT_DIR / f"{int(thr)}_{timestamp}_####.png"))
        return

    py5.redraw()


py5.run_sketch()

