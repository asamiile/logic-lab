import sys
from pathlib import Path

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.deformation_helpers import koch_points

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

upper_limit = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_curve()
    py5.no_loop()


def draw_curve() -> None:
    py5.background(1, 0, 1)
    points = koch_points((0, 250), (500, 250), upper_limit)
    py5.no_fill()
    py5.begin_shape()
    for x_val, y_val in points:
        py5.vertex(x_val, y_val)
    py5.end_shape()


def mouse_clicked() -> None:
    global upper_limit
    upper_limit += 1
    draw_curve()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "koch_deformation_####.png"))


py5.run_sketch()
