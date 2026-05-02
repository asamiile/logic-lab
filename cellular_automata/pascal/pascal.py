from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 8
state = [1]
gen = 0


def setup() -> None:
    py5.size(500, 500)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global gen
    if gen < NUM:
        draw_number(gen)
        update_state()


def draw_number(y_index: int) -> None:
    scalar = py5.width / NUM
    x_pos = (py5.width - len(state) * scalar) * 0.5
    y_pos = y_index * scalar

    py5.fill(0)
    py5.text_size(scalar * 0.5)
    for cell in state:
        py5.text(str(cell), x_pos + scalar * 0.5, y_pos + scalar * 0.5)
        x_pos += scalar


def update_state() -> None:
    global state, gen
    padded = [0, *state, 0]
    state = [padded[i + 1] + padded[i] for i in range(len(padded) - 1)]
    gen += 1


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pascal_####.png"))


py5.run_sketch()

