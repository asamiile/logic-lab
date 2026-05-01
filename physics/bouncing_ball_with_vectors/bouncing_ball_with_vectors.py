from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

position: py5.Py5Vector
velocity: py5.Py5Vector


def setup() -> None:
    global position, velocity
    py5.size(640, 240)
    position = py5.Py5Vector(100, 100)
    velocity = py5.Py5Vector(2.5, 2)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global position, velocity
    py5.background(255)

    position += velocity

    if position.x > py5.width or position.x < 0:
        velocity.x *= -1
    if position.y > py5.height or position.y < 0:
        velocity.y *= -1

    py5.stroke(0)
    py5.fill(127)
    py5.stroke_weight(2)
    py5.circle(position.x, position.y, 48)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "bouncing_ball_with_vectors_####.png"))


py5.run_sketch()
