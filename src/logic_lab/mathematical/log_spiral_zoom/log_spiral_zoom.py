from math import pow
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

STEP = 2 * py5.PI * 0.01


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(1, 0, 1)
    draw_log_spiral()


def draw_log_spiral() -> None:
    theta = 0.0
    scalar = pow(10, py5.mouse_x / py5.width) * py5.height / 2

    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    for _ in range(2000):
        py5.line(
            scalar * rad(theta) * py5.cos(theta),
            scalar * rad(theta) * py5.sin(theta),
            scalar * rad(theta + STEP) * py5.cos(theta + STEP),
            scalar * rad(theta + STEP) * py5.sin(theta + STEP),
        )
        theta -= STEP
    py5.pop_matrix()


def rad(t: float) -> float:
    return pow(1.1, t)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "log_spiral_zoom_####.png"))


py5.run_sketch()

