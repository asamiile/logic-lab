import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def hilbert(n: int, x: float, y: float, xi: float, xj: float, yi: float, yj: float) -> list[tuple]:
    points = []
    if n <= 0:
        return [(x + (xi + yi) / 2, y + (xj + yj) / 2)]

    points.extend(hilbert(n - 1, x, y, yi / 2, yj / 2, xi / 2, xj / 2))
    points.extend(hilbert(n - 1, x + xi / 2, y + xj / 2, xi / 2, xj / 2, yi / 2, yj / 2))
    points.extend(
        hilbert(n - 1, x + xi / 2 + yi / 2, y + xj / 2 + yj / 2, xi / 2, xj / 2, yi / 2, yj / 2)
    )
    points.extend(
        hilbert(n - 1, x + xi / 2 + yi, y + xj / 2 + yj, -yi / 2, -yj / 2, -xi / 2, -xj / 2)
    )

    return points


def setup() -> None:
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_hilbert()


def draw_hilbert() -> None:
    py5.background(20)
    py5.stroke_weight(2)

    for order in range(2, 7):
        py5.stroke(100 + order * 30, 150, 255 - order * 30)
        points = hilbert(order, 50, 50, 900, 0, 0, 900)

        for i in range(len(points) - 1):
            py5.line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hilbert_curve_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
