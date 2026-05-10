import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
points: list[tuple] = [(0, 0)]


def setup() -> None:
    py5.size(1000, 1000)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global points
    py5.background(20)
    py5.stroke_weight(1)
    py5.stroke(100, 200, 100)
    py5.no_fill()

    # Barnsley fern IFS
    transforms = [
        (0.0, 0.0, 0.0, 0.16, 0.0, 0.0),
        (0.85, 0.04, -0.04, 0.85, 0.0, 1.6),
        (0.2, -0.26, 0.23, 0.22, 0.0, 1.6),
        (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44),
    ]

    for _ in range(100):
        a, b, c, d, e, f = random.choice(transforms)
        x, y = points[-1]
        new_x = a * x + b * y + e
        new_y = c * x + d * y + f
        points.append((new_x, new_y))

    for x, y in points[-1000:]:
        px = py5.width / 2 + x * 50
        py_val = y * 50
        if 0 <= px < py5.width and 0 <= py_val < py5.height:
            py5.point(px, py_val)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "iterated_function_systems_####.png"))


py5.run_sketch()
