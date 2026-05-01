from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
segments: list["KochLine"] = []


class KochLine:
    def __init__(self, a: py5.Py5Vector, b: py5.Py5Vector) -> None:
        self.start = a.copy
        self.end = b.copy

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.line(self.start.x, self.start.y, self.end.x, self.end.y)

    def koch_points(self) -> tuple[py5.Py5Vector, py5.Py5Vector, py5.Py5Vector, py5.Py5Vector, py5.Py5Vector]:
        a = self.start.copy
        e = self.end.copy
        v = self.end - self.start
        v *= 1 / 3
        b = a + v
        d = b + v
        v.rotate(-py5.PI / 3)
        c = b + v
        return a, b, c, d, e


def setup() -> None:
    py5.size(640, 240)
    start = py5.Py5Vector(0, 200)
    end = py5.Py5Vector(py5.width, 200)
    segments.append(KochLine(start, end))

    for _ in range(5):
        generate()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    for segment in segments:
        segment.show()
    py5.no_loop()


def generate() -> None:
    global segments
    next_segments: list[KochLine] = []
    for segment in segments:
        a, b, c, d, e = segment.koch_points()
        next_segments.append(KochLine(a, b))
        next_segments.append(KochLine(b, c))
        next_segments.append(KochLine(c, d))
        next_segments.append(KochLine(d, e))
    segments = next_segments


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "koch_curve_####.png"))


py5.run_sketch()
