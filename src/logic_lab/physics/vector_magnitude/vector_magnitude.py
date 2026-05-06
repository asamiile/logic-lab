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

    m = mouse.mag
    py5.fill(0)
    py5.rect(10, 10, m, 10)

    py5.translate(py5.width / 2, py5.height / 2)
    py5.line(0, 0, mouse.x, mouse.y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "vector_magnitude_####.png"))


py5.run_sketch()
