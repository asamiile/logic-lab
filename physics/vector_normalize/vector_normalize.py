from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
    center = py5.Py5Vector(py5.width / 2, py5.height / 2)
    mouse -= center

    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke(200)
    py5.stroke_weight(2)
    py5.line(0, 0, mouse.x, mouse.y)

    mouse = mouse.norm
    mouse *= 50

    py5.stroke(0)
    py5.stroke_weight(8)
    py5.line(0, 0, mouse.x, mouse.y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "vector_normalize_####.png"))


py5.run_sketch()
