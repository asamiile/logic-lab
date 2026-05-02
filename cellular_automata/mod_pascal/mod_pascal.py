from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 250
mod = 2
state = [1]
gen = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    py5.background(0, 0, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global gen
    if gen < NUM:
        draw_cell(gen)
        update_state()


def draw_cell(y_index: int) -> None:
    scalar = py5.width / NUM
    x_pos = (py5.width - len(state) * scalar) * 0.5
    y_pos = y_index * scalar

    py5.no_stroke()
    for cell in state:
        py5.fill(cell / mod, cell / mod, 1)
        py5.rect(x_pos, y_pos, scalar, scalar)
        x_pos += scalar


def update_state() -> None:
    global state, gen
    padded = [0, *state, 0]
    state = [(padded[i + 1] + padded[i]) % mod for i in range(len(padded) - 1)]
    gen += 1


def mouse_clicked() -> None:
    global state, gen, mod
    gen = 0
    state = [1]
    mod = int(py5.random(2, 20))
    print(mod)
    py5.background(0, 0, 1)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mod_pascal_####.png"))


py5.run_sketch()

