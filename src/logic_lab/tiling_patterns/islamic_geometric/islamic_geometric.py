import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_islamic()


def draw_islamic() -> None:
    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    py5.stroke_weight(2)
    py5.stroke(100, 200, 150)
    py5.no_fill()

    for i in range(12):
        angle = i * 2 * math.pi / 12
        x = 300 * math.cos(angle)
        y = 300 * math.sin(angle)

        py5.push_matrix()
        py5.translate(x, y)
        py5.rotate(angle)

        size = 80
        for j in range(4):
            py5.stroke(100 + j * 40, 200, 150)
            py5.rect(-size / 2, -size / 2, size, size)
            size *= 0.6

        py5.pop_matrix()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "islamic_geometric_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
