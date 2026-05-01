from math import acos
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def angle_between(v1: py5.Py5Vector, v2: py5.Py5Vector) -> float:
    mag = v1.mag * v2.mag
    if mag == 0:
        return 0.0
    dot = v1.x * v2.x + v1.y * v2.y
    return acos(max(-1.0, min(1.0, dot / mag)))


def draw_vector(v: py5.Py5Vector, pos: py5.Py5Vector) -> None:
    arrow_size = 6
    with py5.push_matrix():
        py5.translate(pos.x, pos.y)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.rotate(v.heading)
        length = v.mag
        py5.line(0, 0, length, 0)
        py5.line(length, 0, length - arrow_size, +arrow_size / 2)
        py5.line(length, 0, length - arrow_size, -arrow_size / 2)


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    mouse_pos = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
    center_pos = py5.Py5Vector(py5.width / 2, py5.height / 2)

    diff = mouse_pos - center_pos
    v = diff.norm * 100 if diff.mag > 0 else py5.Py5Vector(100, 0)
    x_axis = py5.Py5Vector(100, 0)

    draw_vector(v, center_pos)
    draw_vector(x_axis, center_pos)

    theta = angle_between(v, x_axis)

    py5.fill(0)
    py5.text_size(32)
    py5.text(f"{int(py5.degrees(theta))} degrees\n{theta:.2f} radians", 10, 160)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "angle_between_####.png"))


py5.run_sketch()
