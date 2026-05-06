from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 250
mod = 2
state = [1]
gen = 0


def setup() -> None:
    py5.size(1000, 500)
    py5.color_mode(py5.HSB, 1)
    py5.background(0, 0, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global gen
    if gen < NUM:
        draw_cell(gen)
        update_state()


def draw_cell(y_index: int) -> None:
    scalar = py5.width * 0.5 / NUM
    x_pos = (py5.width - len(state) * scalar) * 0.5
    y_pos = y_index * scalar

    py5.no_stroke()
    for cell in state:
        py5.fill(cell / mod, cell / mod, 1)
        py5.rect(x_pos, y_pos, scalar, scalar)
        x_pos += scalar


def transition(a: int, b: int, c: int) -> int:
    return (a + b + c) % mod


def update_state() -> None:
    global state, gen
    padded = [0, 0, *state, 0, 0]
    next_state = [
        transition(padded[i - 1], padded[i], padded[i + 1]) for i in range(1, len(padded) - 1)
    ]
    state = next_state
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
        py5.save_frame(str(SCREENSHOT_DIR / "ca_1dim_####.png"))


py5.run_sketch()
