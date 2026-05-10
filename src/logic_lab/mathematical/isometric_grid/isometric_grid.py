import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
time_value = 0.0


def setup() -> None:
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value
    py5.background(25)
    time_value += 0.02

    grid_size = 40
    cols = 12
    rows = 10

    py5.stroke_weight(1)
    py5.stroke(100, 200, 150)
    py5.no_fill()

    for row in range(rows):
        for col in range(cols):
            height = 30 * math.sin((col + row) * 0.3 + time_value) + 30
            draw_isometric_cube(col * grid_size, row * grid_size, height)


def draw_isometric_cube(x: float, y: float, height: float) -> None:
    iso_x = x - y
    iso_y = (x + y) * 0.5 - height

    size = 20
    py5.line(iso_x, iso_y, iso_x + size, iso_y)
    py5.line(iso_x, iso_y, iso_x + size / 2, iso_y - size / 2)
    py5.line(iso_x + size, iso_y, iso_x + size + size / 2, iso_y - size / 2)
    py5.line(iso_x + size / 2, iso_y - size / 2, iso_x + size + size / 2, iso_y - size / 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "isometric_grid_####.png"))


py5.run_sketch()
