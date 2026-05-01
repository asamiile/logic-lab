from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
angle = 0.0


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global angle
    py5.background(255)
    angle = py5.remap(py5.mouse_x, 0, py5.width, 0, py5.HALF_PI)
    py5.translate(py5.width / 2, py5.height)
    py5.stroke(0)
    py5.stroke_weight(2)
    branch(80)


def branch(length: float) -> None:
    py5.line(0, 0, 0, -length)
    py5.translate(0, -length)
    length *= 0.67

    if length > 2:
        py5.push_matrix()
        py5.rotate(angle)
        branch(length)
        py5.pop_matrix()

        py5.push_matrix()
        py5.rotate(-angle)
        branch(length)
        py5.pop_matrix()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "tree_####.png"))


py5.run_sketch()
