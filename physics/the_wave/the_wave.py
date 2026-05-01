from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

ANGLE_VELOCITY = 0.2
SPACING = 24

start_angle = 0.0


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global start_angle
    py5.background(255)

    angle = start_angle
    start_angle += 0.02

    for x in range(0, py5.width + 1, SPACING):
        y = py5.remap(py5.sin(angle), -1, 1, 0, py5.height)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127, 127)
        py5.circle(x, y, 48)
        angle += ANGLE_VELOCITY


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "the_wave_####.png"))


py5.run_sketch()
