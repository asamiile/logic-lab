import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
time_value = 0.0


def setup() -> None:
    py5.size(1000, 800)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value
    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    py5.stroke_weight(2)
    py5.no_fill()

    # Ellipse
    py5.stroke(255, 100, 100)
    a = 150 + 50 * math.sin(time_value)
    b = 100 + 40 * math.cos(time_value * 0.7)
    draw_ellipse(a, b)

    # Parabola
    py5.stroke(100, 255, 100)
    p = 100 + 30 * math.sin(time_value * 0.8)
    draw_parabola(p)

    # Hyperbola
    py5.stroke(100, 100, 255)
    a = 120 + 40 * math.cos(time_value * 0.6)
    b = 100 + 30 * math.sin(time_value * 0.5)
    draw_hyperbola(a, b)


def draw_ellipse(a: float, b: float) -> None:
    for t in [i * 0.01 for i in range(629)]:
        x = a * math.cos(t)
        y = b * math.sin(t)
        py5.point(x, y)


def draw_parabola(p: float) -> None:
    for y in range(-300, 301, 5):
        x = (y * y) / (4 * p)
        py5.point(x, y)


def draw_hyperbola(a: float, b: float) -> None:
    for y in range(-300, 301, 3):
        if abs(y) >= 20:
            x_pos = a * math.sqrt(1 + (y * y) / (b * b))
            py5.point(x_pos, y)
            py5.point(-x_pos, y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "conic_sections_####.png"))


py5.run_sketch()
