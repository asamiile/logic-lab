from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

r = 0.0
theta = 0.0


def setup() -> None:
    py5.size(640, 240)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global r, theta

    x = r * py5.cos(theta)
    y = r * py5.sin(theta)

    py5.no_stroke()
    py5.fill(0)
    py5.circle(x + py5.width / 2, y + py5.height / 2, 16)

    theta += 0.01
    r += 0.05


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spiral_####.png"))


py5.run_sketch()
