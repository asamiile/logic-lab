from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

num_a = 10
num_b = 6
ratio = num_b / num_a
thr = 160.0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_current()
    py5.no_loop()


def draw_current() -> None:
    py5.background(0, 0, 1)
    py5.stroke(0)
    div_square(0, 0, py5.width)


def div_square(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = wd + x_pos
    y_end_pos = wd + y_pos
    py5.fill(py5.random(1), 1, 1)
    py5.rect(x_pos, y_pos, wd, wd)

    while wd > thr:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd * ratio < x_end_pos + 0.1:
                div_rect(x_pos, y_pos, wd * ratio)
                x_pos += wd * ratio
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd / ratio < y_end_pos + 0.1:
                div_rect(x_pos, y_pos, wd)
                y_pos += wd / ratio
            wd = y_end_pos - y_pos


def div_rect(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = x_pos + wd
    y_end_pos = y_pos + wd / ratio
    py5.fill(py5.random(1), 1, 1)
    py5.rect(x_pos, y_pos, wd, wd / ratio)

    while wd > thr:
        itr += 1
        if itr % 2 == 0:
            while x_pos + wd < x_end_pos + 0.1:
                div_square(x_pos, y_pos, wd)
                x_pos += wd
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd < y_end_pos + 0.1:
                div_square(x_pos, y_pos, wd)
                y_pos += wd
            wd = y_end_pos - y_pos


def mouse_clicked() -> None:
    global num_a, num_b, ratio, thr
    num_a = int(py5.random(1, 20))
    num_b = int(py5.random(1, 20))
    while num_a == num_b:
        num_b = int(py5.random(1, 20))
    thr = int(py5.random(10, 300))
    ratio = num_a / num_b
    print("numA =", num_a, "numB =", num_b, "thr =", thr)
    draw_current()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "euclid_recur_div_square_####.png"))


py5.run_sketch()

