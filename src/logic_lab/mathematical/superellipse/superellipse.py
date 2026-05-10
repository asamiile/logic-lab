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
    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke_weight(2)
    py5.no_fill()

    time_value += 0.01

    n = 2.0 + 3.0 * (1.0 + math.sin(time_value)) / 2.0
    a, b = 200, 150

    for i in range(628):
        t = i * 0.01
        x = a * math.copysign(abs(math.cos(t)) ** (2 / n), math.cos(t))
        y = b * math.copysign(abs(math.sin(t)) ** (2 / n), math.sin(t))

        hue = (i / 628.0 * 255) % 255
        py5.stroke(hue, 255, 255)
        py5.point(x, y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "superellipse_####.png"))


py5.run_sketch()
