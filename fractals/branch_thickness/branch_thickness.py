from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

angle: float = 0


def branch(length: float) -> None:
    # Stroke weight decreases with branch length
    # map(value, start1, stop1, start2, stop2) = (value - start1) / (stop1 - start1) * (stop2 - start2) + start2
    stroke_width = (length - 2) / (120 - 2) * (16 - 1) + 1
    py5.stroke_weight(stroke_width)

    py5.line(0, 0, 0, -length)
    py5.translate(0, -length)

    # Each branch shrinks to 2/3 of previous length
    length *= 0.67

    if length > 2:
        py5.push()
        py5.rotate(angle)
        branch(length)
        py5.pop()

        py5.push()
        py5.rotate(-angle)
        branch(length)
        py5.pop()


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global angle
    py5.background(255)

    # Map angle from 0 to HALF_PI (90°) based on mouse X position
    angle = (py5.mouse_x - 0) / (py5.width - 0) * (py5.HALF_PI - 0) + 0

    # Start tree from bottom center
    py5.translate(py5.width / 2, py5.height)
    py5.stroke(0)
    branch(80)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "branch_thickness_####.png"))


py5.run_sketch()
