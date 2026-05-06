from math import atan, pow, sqrt
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

gap = 0.2
vec: list[tuple[float, float]] = []


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.background(255)
    reset_vectors()
    draw_log_spiral()


def draw() -> None:
    global vec
    py5.stroke(0)
    py5.stroke_weight(1)
    draw_square(vec)
    vec = get_vector(vec)


def reset_vectors() -> None:
    global vec
    vec = [
        (0, 0),
        (py5.width, 0),
        (py5.width, py5.height),
        (0, py5.height),
    ]


def draw_log_spiral() -> None:
    if gap <= 0 or gap >= 1:
        return

    step = 2 * py5.PI * 0.001
    b = sqrt(2 * gap * gap - 2 * gap + 1)
    c = atan(gap / (1 - gap))
    v_x = -py5.width / 2
    v_y = -py5.height / 2

    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke(255, 0, 0)
    py5.stroke_weight(3)
    while magnitude(v_x, v_y) > 1:
        next_x, next_y = rotate(v_x, v_y, step)
        scale = pow(b, step / c)
        next_x *= scale
        next_y *= scale
        py5.line(v_x, v_y, next_x, next_y)
        v_x, v_y = next_x, next_y
    py5.pop_matrix()


def draw_square(points: list[tuple[float, float]]) -> None:
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        py5.line(x1, y1, x2, y2)


def get_vector(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    next_vec = []
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        next_vec.append((x1 + (x2 - x1) * gap, y1 + (y2 - y1) * gap))
    return next_vec


def rotate(x_val: float, y_val: float, angle: float) -> tuple[float, float]:
    return (
        x_val * py5.cos(angle) - y_val * py5.sin(angle),
        x_val * py5.sin(angle) + y_val * py5.cos(angle),
    )


def magnitude(x_val: float, y_val: float) -> float:
    return sqrt(x_val * x_val + y_val * y_val)


def mouse_clicked() -> None:
    global gap
    py5.background(255)
    gap = py5.random(1) / 2
    print("gap =", gap)
    reset_vectors()
    draw_log_spiral()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recur_square_spiral_####.png"))


py5.run_sketch()
