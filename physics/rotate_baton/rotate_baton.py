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

    py5.fill(127)
    py5.stroke(0)
    py5.rect_mode(py5.CENTER)
    py5.translate(py5.width / 2, py5.height / 2)
    py5.rotate(angle)
    py5.line(-50, 0, 50, 0)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.fill(127)
    py5.circle(50, 0, 16)
    py5.circle(-50, 0, 16)

    angle += 0.1


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "rotate_baton_####.png"))


py5.run_sketch()
