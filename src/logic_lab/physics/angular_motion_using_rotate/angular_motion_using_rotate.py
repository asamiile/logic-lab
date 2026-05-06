from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

angle = 0.0
angle_velocity = 0.0
angle_acceleration = 0.0001


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global angle, angle_velocity
    py5.background(255)

    py5.translate(py5.width / 2, py5.height / 2)
    py5.rotate(angle)

    py5.stroke(0)
    py5.stroke_weight(2)
    py5.fill(127)

    py5.line(-60, 0, 60, 0)
    py5.circle(60, 0, 16)
    py5.circle(-60, 0, 16)

    angle_velocity += angle_acceleration
    angle += angle_velocity


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "angular_motion_using_rotate_####.png"))


py5.run_sketch()
