from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

NUM = 250
state = [1]
rule = [0, 0, 0, 1, 1, 1, 1, 0]
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
        py5.fill(0, 0, 1 - cell)
        py5.rect(x_pos, y_pos, scalar, scalar)
        x_pos += scalar


def transition(a: int, b: int, c: int) -> int:
    rule_int = a * 4 + b * 2 + c
    return rule[7 - rule_int]


def update_state() -> None:
    global state, gen
    padded = [0, 0, *state, 0, 0]
    state = [transition(padded[i - 1], padded[i], padded[i + 1]) for i in range(1, len(padded) - 1)]
    gen += 1


def mouse_clicked() -> None:
    global state, gen, rule
    gen = 0
    state = [1]
    rule = []
    rule_int = 0
    for i in range(8):
        value = int(py5.random(2))
        rule.append(value)
        rule_int += value * int(py5.pow(2, 7 - i))
    print(rule_int)
    py5.background(0, 0, 1)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "elementary_ca_####.png"))


py5.run_sketch()

