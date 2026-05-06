from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Default values (matching original slider defaults)
SPREAD = 0.25
BASE_SIZE = 20 / 240  # sizeSlider / height
SIZE_SPREAD = 0.01
BASE_HUE = 250.0
HUE_SPREAD = 15.0
ALPHA = 0.75


def setup() -> None:
    py5.size(640, 240)
    py5.color_mode(py5.HSB, 360, 100, 100, 1)
    py5.background(97, 0, 97)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.translate(py5.width / 2, py5.height / 2)
    py5.scale(py5.height / 2)

    x = py5.random_gaussian(0, SPREAD)
    y = py5.random_gaussian(0, SPREAD)
    size = py5.random_gaussian(BASE_SIZE, SIZE_SPREAD)
    if size <= 0:
        size = 0.001

    paint_hue = py5.random_gaussian(BASE_HUE, HUE_SPREAD) % 360
    paint_sat = min(py5.random_gaussian(80, 20), 100)
    paint_bright = min(py5.random_gaussian(80, 20), 100)

    py5.no_stroke()
    py5.fill(paint_hue, paint_sat, paint_bright, ALPHA)
    py5.ellipse(x, y, size, size)


def key_pressed() -> None:
    if py5.key == " ":
        py5.background(97, 0, 97)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "paint_splatter_####.png"))


py5.run_sketch()
