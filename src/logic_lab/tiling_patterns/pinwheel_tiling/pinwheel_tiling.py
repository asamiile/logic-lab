import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 1000)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_pinwheel()


def draw_pinwheel() -> None:
    py5.stroke_weight(1)

    def draw_triangle(x: float, y: float, size: float, angle: float, depth: int) -> None:
        if depth == 0:
            return

        py5.push_matrix()
        py5.translate(x, y)
        py5.rotate(angle)

        color_val = (255 - depth * 30) % 256
        py5.stroke(color_val, 150, 255 - color_val)
        py5.triangle(0, 0, size, 0, size / 2, size * math.sqrt(3) / 2)

        draw_triangle(size / 2, 0, size / 2, angle + math.pi / 5, depth - 1)
        draw_triangle(
            size * 0.75, size * math.sqrt(3) / 4, size / 2, angle - math.pi / 5, depth - 1
        )

        py5.pop_matrix()

    draw_triangle(py5.width / 2, py5.height / 2, 200, 0, 5)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pinwheel_tiling_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
