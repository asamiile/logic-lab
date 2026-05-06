import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

segments: list["KochLine"] = []


class KochLine:
    def __init__(self, a: py5.Py5Vector, b: py5.Py5Vector) -> None:
        # Start and end points
        self.a = py5.Py5Vector(a.x, a.y)
        self.b = py5.Py5Vector(b.x, b.y)

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.line(self.a.x, self.a.y, self.b.x, self.b.y)

    def koch_a(self) -> py5.Py5Vector:
        return py5.Py5Vector(self.a.x, self.a.y)

    def koch_b(self) -> py5.Py5Vector:
        # 1/3 of the way from a to b
        v = self.b - self.a
        v *= 1.0 / 3.0
        return self.a + v

    def koch_c(self) -> py5.Py5Vector:
        # Start at a
        a = py5.Py5Vector(self.a.x, self.a.y)

        # Move 1/3 of the way to b
        v = self.b - self.a
        v *= 1.0 / 3.0
        a += v

        # Rotate by -PI/3 (negative so it rotates "up")
        angle = -math.pi / 3.0
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotated_x = v.x * cos_a - v.y * sin_a
        rotated_y = v.x * sin_a + v.y * cos_a
        a += py5.Py5Vector(rotated_x, rotated_y)

        return a

    def koch_d(self) -> py5.Py5Vector:
        # 2/3 of the way from a to b
        v = self.b - self.a
        v *= 2.0 / 3.0
        return self.a + v

    def koch_e(self) -> py5.Py5Vector:
        return py5.Py5Vector(self.b.x, self.b.y)


def generate() -> None:
    global segments
    next_segments = []

    for segment in segments:
        a = segment.koch_a()
        b = segment.koch_b()
        c = segment.koch_c()
        d = segment.koch_d()
        e = segment.koch_e()

        next_segments.append(KochLine(a, b))
        next_segments.append(KochLine(b, c))
        next_segments.append(KochLine(c, d))
        next_segments.append(KochLine(d, e))

    segments = next_segments


def setup() -> None:
    py5.size(640, 240)

    w = 200
    offset = (py5.width - w) / 2
    y = 62
    a = py5.Py5Vector(offset, y)
    b = py5.Py5Vector(py5.width - offset, y)
    c = py5.Py5Vector(py5.width / 2, y + w * math.cos(math.pi / 6))

    segments.append(KochLine(a, b))
    segments.append(KochLine(b, c))
    segments.append(KochLine(c, a))

    # Apply Koch rules 5 times
    for _ in range(5):
        generate()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    for segment in segments:
        segment.show()
    py5.no_loop()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "koch_snowflake_####.png"))


py5.run_sketch()
