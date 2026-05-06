from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 250
mod = 4
state: list[list[int]] = []


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    initialize()
    py5.frame_rate(2)


def draw() -> None:
    draw_cell()
    update_state()


def initialize() -> None:
    global state
    state = [[0 for _ in range(NUM)] for _ in range(NUM)]
    state[NUM // 2][NUM // 2] = 1


def draw_cell() -> None:
    scalar = py5.height / NUM
    py5.no_stroke()
    for i in range(NUM):
        y_pos = i * scalar
        for j in range(NUM):
            x_pos = j * scalar
            cell = state[i][j]
            py5.fill(cell / mod, cell / mod, 1)
            py5.rect(x_pos, y_pos, scalar, scalar)


def transition(i: int, j: int) -> int:
    next_cell = (
        state[(i - 1 + NUM) % NUM][j]
        + state[i][(j - 1 + NUM) % NUM]
        + state[i][j]
        + state[i][(j + 1) % NUM]
        + state[(i + 1) % NUM][j]
    )
    return next_cell % mod


def update_state() -> None:
    global state
    next_state = [[0 for _ in range(NUM)] for _ in range(NUM)]
    for i in range(NUM):
        for j in range(NUM):
            next_state[i][j] = transition(i, j)
    state = next_state


def mouse_clicked() -> None:
    global mod
    initialize()
    mod = int(py5.random(2, 20))
    print(mod)
    py5.background(0, 0, 1)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ca_2dim_####.png"))


py5.run_sketch()

