from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM_A = 10
NUM_B = 6
RATIO = NUM_B / NUM_A


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_division()
    py5.no_loop()


def draw_division() -> None:
    itr = 0
    x_pos = 0.0
    y_pos = 0.0
    wd = py5.width * RATIO

    py5.background(0, 0, 1)
    py5.stroke(0)

    while wd > 0.1:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd < py5.width + 0.1:
                div_square(x_pos, y_pos, wd)
                x_pos += wd
            wd = py5.width - x_pos
        else:
            while y_pos + wd < py5.width * RATIO + 0.1:
                div_square(x_pos, y_pos, wd)
                y_pos += wd
            wd = py5.width * RATIO - y_pos


def div_square(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = wd + x_pos
    y_end_pos = wd + y_pos

    while wd > 0.1:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd * RATIO < x_end_pos + 0.1:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd * RATIO, wd)
                x_pos += wd * RATIO
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd / RATIO < y_end_pos + 0.1:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd, wd / RATIO)
                y_pos += wd / RATIO
            wd = y_end_pos - y_pos


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "euclid_rect_div_rect_####.png"))


py5.run_sketch()

