import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def draw_rep_tile(x: float, y: float, size: float, depth: int) -> None:
    if depth == 0 or size < 2:
        py5.rect(x, y, size, size)
        return

    new_size = size / math.sqrt(2)

    for i in range(2):
        for j in range(2):
            draw_rep_tile(x + i * size / 2, y + j * size / 2, new_size, depth - 1)


def setup() -> None:
    py5.size(1000, 1000)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_reptiles()


def draw_reptiles() -> None:
    py5.stroke_weight(1)
    py5.no_fill()

    for i in range(3):
        for j in range(3):
            py5.stroke(100 + i * 50, 150 + j * 30, 255)
            draw_rep_tile(i * 330, j * 330, 320, 4)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "rep_tiles_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
