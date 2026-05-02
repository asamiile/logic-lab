from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM_A = 10
NUM_B = 6
SCALAR = 50


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_division()
    py5.no_loop()


def draw_division() -> None:
    num_a = NUM_A * SCALAR
    num_b = NUM_B * SCALAR
    wd = num_b
    x_pos = 0
    y_pos = 0
    itr = 0

    py5.background(0, 0, 1)
    py5.stroke(0)

    while wd > 0:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd <= num_a:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd, wd)
                x_pos += wd
            wd = num_a - x_pos
        else:
            while y_pos + wd <= num_b:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd, wd)
                y_pos += wd
            wd = num_b - y_pos


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "euclid_div_rect_color_####.png"))


py5.run_sketch()

