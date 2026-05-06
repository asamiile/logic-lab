from math import pow, sqrt
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

fibo = [0, 1, 1]
SGN = [-1, 1, 1, -1]


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_current()
    py5.no_loop()


def draw_current() -> None:
    py5.background(255)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke(0)
    draw_fibo_spiral()
    py5.stroke(255, 0, 0)
    draw_gold_spiral()
    py5.pop_matrix()


def draw_fibo_spiral() -> None:
    x_pos = 0.0
    y_pos = 0.0
    scalar = py5.width / (2 * fibo[-1])

    for i in range(1, len(fibo) - 1):
        py5.rect(
            scalar * x_pos,
            scalar * y_pos,
            scalar * SGN[(i + 1) % 4] * fibo[i],
            scalar * SGN[i % 4] * fibo[i],
        )
        py5.arc(
            scalar * (x_pos + SGN[(i + 1) % 4] * fibo[i]),
            scalar * (y_pos + SGN[i % 4] * fibo[i]),
            scalar * 2 * fibo[i],
            scalar * 2 * fibo[i],
            (1 + i) * py5.PI / 2,
            (2 + i) * py5.PI / 2,
        )
        if i % 2 == 1:
            x_pos += SGN[i % 4] * (fibo[i] + fibo[i + 1])
        else:
            y_pos += SGN[i % 4] * (fibo[i] + fibo[i + 1])


def draw_gold_spiral() -> None:
    scalar = py5.width / (2 * fibo[-1])
    phi = (1 + sqrt(5)) / 2
    step = -py5.PI / 50
    origin_x = 1.0
    origin_y = 1.0
    v_x = 0.0
    v_y = 1.0

    for i in range(1, len(fibo) - 1):
        v_x += SGN[i % 4] * fibo[i]
        v_y += SGN[(i - 1) % 4] * fibo[i]

    v_x = (v_x - origin_x) * scalar
    v_y = (v_y - origin_y) * scalar

    py5.push_matrix()
    py5.translate(scalar, scalar)
    for _ in range((len(fibo) - 2) * 25):
        next_x, next_y = rotate(v_x, v_y, step)
        scale = pow(phi, 2 * step / py5.PI)
        next_x *= scale
        next_y *= scale
        py5.line(v_x, v_y, next_x, next_y)
        v_x, v_y = next_x, next_y
    py5.pop_matrix()


def rotate(x_val: float, y_val: float, angle: float) -> tuple[float, float]:
    return (
        x_val * py5.cos(angle) - y_val * py5.sin(angle),
        x_val * py5.sin(angle) + y_val * py5.cos(angle),
    )


def mouse_clicked() -> None:
    next_fibo = fibo[-2] + fibo[-1]
    fibo.append(next_fibo)
    print(next_fibo)
    draw_current()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "gold_fibo_spiral_####.png"))


py5.run_sketch()

