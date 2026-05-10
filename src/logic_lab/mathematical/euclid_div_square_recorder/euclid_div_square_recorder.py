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
    py5.save(SCREENSHOT_DIR / f"{NUM_A}_{NUM_B}.png")
    py5.no_loop()


def draw_division() -> None:
    wd = py5.width
    x_pos = 0.0
    y_pos = 0.0
    itr = 0

    py5.background(0, 0, 1)
    py5.stroke(0)

    while wd > 0.1:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd * RATIO < py5.width + 0.1:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd * RATIO, wd)
                x_pos += wd * RATIO
            wd = py5.width - x_pos
        else:
            while y_pos + wd / RATIO < py5.width + 0.1:
                py5.fill(py5.random(1), 1, 1)
                py5.rect(x_pos, y_pos, wd, wd / RATIO)
                y_pos += wd / RATIO
            wd = py5.width - y_pos


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "euclid_div_square_recorder_####.png"))


py5.run_sketch()
