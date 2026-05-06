from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(640, 240)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    x = py5.random_gaussian(320, 60)

    py5.no_stroke()
    py5.fill(0, 10)
    py5.circle(x, 120, 16)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "gaussian_distribution_####.png"))


py5.run_sketch()
