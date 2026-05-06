from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

CELL_SIZE = 10
RULESET = [0, 1, 0, 1, 1, 0, 1, 0]  # Rule 90

cells: list[int] = []
generation = 0


def setup() -> None:
    global cells, generation
    py5.size(640, 240)
    py5.background(255)

    cell_count = py5.floor(py5.width / CELL_SIZE)
    cells = [0] * cell_count
    cells[py5.floor(cell_count / 2)] = 1
    generation = 0

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global cells, generation
    for i in range(1, len(cells) - 1):
        if cells[i] == 1:
            py5.fill(0)
            py5.square(i * CELL_SIZE, generation * CELL_SIZE, CELL_SIZE)

    nextgen = cells.copy()
    for i in range(1, len(cells) - 1):
        left = cells[i - 1]
        me = cells[i]
        right = cells[i + 1]
        nextgen[i] = rules(left, me, right)
    cells = nextgen

    generation += 1
    if generation * CELL_SIZE > py5.height:
        py5.no_loop()


def rules(a: int, b: int, c: int) -> int:
    index = int(f"{a}{b}{c}", 2)
    return RULESET[7 - index]


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "elementary_wolfram_ca_####.png"))


py5.run_sketch()
