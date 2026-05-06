from math import sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 200
MOD = 10
scalar = 0.0
state: list[list[int]] = []
lattice: list[list[tuple[float, float]]] = []
base0 = (0.0, 1.0)
base1 = (0.0, 0.0)


def setup() -> None:
    global scalar, base1
    py5.size(693, 800)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    base1 = (py5.cos(py5.PI / 6), py5.sin(py5.PI / 6))
    initialize()
    make_lattice()
    draw_tiling()


def draw() -> None:
    global state
    py5.background(0, 0, 1)
    next_state = [[0 for _ in range(NUM)] for _ in range(NUM)]
    for i in range(NUM):
        for j in range(NUM):
            next_state[i][j] = transition(i, j)
    state = next_state
    draw_tiling()


def initialize() -> None:
    global state
    state = [[0 for _ in range(NUM)] for _ in range(NUM)]
    state[NUM // 2][NUM // 2] = 1


def make_lattice() -> None:
    global lattice
    lattice = []
    for i in range(NUM):
        row = []
        for j in range(NUM):
            x_pos = (base0[0] * i + base1[0] * j) * scalar
            y_pos = ((base0[1] * i + base1[1] * j) * scalar) % py5.height
            row.append((x_pos, y_pos))
        lattice.append(row)


def draw_tiling() -> None:
    py5.no_stroke()
    for i in range(NUM):
        for j in range(NUM):
            x_pos, y_pos = lattice[i][j]
            cell = state[i][j]
            py5.fill(cell / MOD, cell / MOD, 1)
            draw_hex_tile(x_pos, y_pos)


def draw_hex_tile(x_pos: float, y_pos: float) -> None:
    radius = scalar / sqrt(3)
    py5.begin_shape()
    for i in range(6):
        angle = py5.TWO_PI * i / 6
        py5.vertex(x_pos + py5.cos(angle) * radius, y_pos + py5.sin(angle) * radius)
    py5.end_shape(py5.CLOSE)


def transition(i: int, j: int) -> int:
    value = (
        state[i][j]
        + state[(i - 1 + NUM) % NUM][j]
        + state[(i - 1 + NUM) % NUM][(j + 1) % NUM]
        + state[i][(j + 1) % NUM]
        + state[(i + 1) % NUM][j]
        + state[(i + 1) % NUM][(j - 1 + NUM) % NUM]
        + state[i][(j - 1 + NUM) % NUM]
    )
    return value % MOD


def mouse_clicked() -> None:
    initialize()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hex_lattice_ca_####.png"))


py5.run_sketch()

