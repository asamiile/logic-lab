from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

AMPLITUDE = 200

angle = 0.0
angle_velocity = 0.05


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global angle
    py5.background(255)

    x = AMPLITUDE * py5.sin(angle)
    angle += angle_velocity

    py5.translate(py5.width / 2, py5.height / 2)

    py5.stroke(0)
    py5.stroke_weight(2)
    py5.fill(127)
    py5.line(0, 0, x, 0)
    py5.circle(x, 0, 48)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "simple_harmonic_motion_ii_####.png"))


py5.run_sketch()
