from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

r1 = 100
r2 = 100
m1 = 10
m2 = 10
a1 = 0.0
a2 = 0.0
a1_v = 0.0
a2_v = 0.0
g = 1

px2 = -1.0
py2 = -1.0
cx = 0.0
cy = 0.0

buffer: py5.Py5Graphics


def setup() -> None:
    global a1, a2, cx, cy, buffer
    py5.size(640, 240)
    a1 = py5.PI / 2
    a2 = py5.PI / 2
    cx = py5.width / 2
    cy = 20
    buffer = py5.create_graphics(py5.width, py5.height)
    buffer.begin_draw()
    buffer.background(255)
    buffer.end_draw()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global a1, a2, a1_v, a2_v, px2, py2
    py5.background(255)
    py5.image_mode(py5.CORNER)
    py5.image(buffer, 0, 0, py5.width, py5.height)

    num1 = -g * (2 * m1 + m2) * py5.sin(a1)
    num2 = -m2 * g * py5.sin(a1 - 2 * a2)
    num3 = -2 * py5.sin(a1 - a2) * m2
    num4 = a2_v * a2_v * r2 + a1_v * a1_v * r1 * py5.cos(a1 - a2)
    den = r1 * (2 * m1 + m2 - m2 * py5.cos(2 * a1 - 2 * a2))
    a1_a = (num1 + num2 + num3 * num4) / den

    num1 = 2 * py5.sin(a1 - a2)
    num2 = a1_v * a1_v * r1 * (m1 + m2)
    num3 = g * (m1 + m2) * py5.cos(a1)
    num4 = a2_v * a2_v * r2 * m2 * py5.cos(a1 - a2)
    den = r2 * (2 * m1 + m2 - m2 * py5.cos(2 * a1 - 2 * a2))
    a2_a = (num1 * (num2 + num3 + num4)) / den

    py5.translate(cx, cy)
    py5.stroke(0)
    py5.stroke_weight(2)

    x1 = r1 * py5.sin(a1)
    y1 = r1 * py5.cos(a1)

    x2 = x1 + r2 * py5.sin(a2)
    y2 = y1 + r2 * py5.cos(a2)

    py5.line(0, 0, x1, y1)
    py5.fill(0)
    py5.ellipse(x1, y1, m1, m1)

    py5.line(x1, y1, x2, y2)
    py5.fill(0)
    py5.ellipse(x2, y2, m2, m2)

    a1_v += a1_a
    a2_v += a2_a
    a1 += a1_v
    a2 += a2_v

    buffer.begin_draw()
    buffer.stroke(0)
    if py5.frame_count > 1:
        buffer.line(px2 + cx, py2 + cy, x2 + cx, y2 + cy)
    buffer.end_draw()

    px2 = x2
    py2 = y2


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "double_pendulum_####.png"))


py5.run_sketch()
