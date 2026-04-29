from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

ANGLE_VELOCITY = 0.2
AMPLITUDE = 100
SPACING = 24


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    py5.background(255)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.fill(127, 127)

    angle = 0.0
    for x in range(0, py5.width + 1, SPACING):
        y = AMPLITUDE * py5.sin(angle)
        py5.circle(x, y + py5.height / 2, 48)
        angle += ANGLE_VELOCITY


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "static_wave_####.png"))


py5.run_sketch()
