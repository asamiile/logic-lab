from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

x = 100.0
y = 100.0
xspeed = 2.5
yspeed = 2.0


def setup() -> None:
    py5.size(640, 240)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global x, y, xspeed, yspeed

    py5.background(255)

    x += xspeed
    y += yspeed

    if x > py5.width or x < 0:
        xspeed *= -1
    if y > py5.height or y < 0:
        yspeed *= -1

    py5.stroke(0)
    py5.fill(127)
    py5.stroke_weight(2)
    py5.circle(x, y, 48)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "bouncing_ball_no_vectors_####.png"))


py5.run_sketch()
