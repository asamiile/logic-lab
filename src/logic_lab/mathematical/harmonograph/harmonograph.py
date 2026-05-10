import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
time_value = 0.0


def setup() -> None:
    py5.size(1000, 800)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value
    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)
    py5.stroke_weight(1)
    py5.stroke(100, 200, 255)
    py5.no_fill()

    time_value += 0.01

    for i in range(int(time_value * 10) % 500):
        t = i * 0.02
        decay = math.exp(-i * 0.002)
        x = decay * (200 * math.sin(t * 0.5) + 150 * math.sin(t * 0.3))
        y = decay * (150 * math.cos(t * 0.7) + 100 * math.cos(t * 0.4))
        py5.point(x, y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "harmonograph_####.png"))


py5.run_sketch()
