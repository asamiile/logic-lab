from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

r = 0.0
theta = 0.0


def setup() -> None:
    global r
    py5.size(640, 240)
    r = py5.height * 0.45
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global theta
    py5.background(255)

    py5.translate(py5.width / 2, py5.height / 2)

    x = r * py5.cos(theta)
    y = r * py5.sin(theta)

    py5.fill(127)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.line(0, 0, x, y)
    py5.circle(x, y, 48)

    theta += 0.02


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "polar_to_cartesian_####.png"))


py5.run_sketch()
