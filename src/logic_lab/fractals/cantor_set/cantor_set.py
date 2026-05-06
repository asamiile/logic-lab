from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(640, 120)
    py5.background(255)
    py5.stroke_weight(2)
    cantor(10, 10, 620)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.no_loop()


def cantor(x: float, y: float, length: float) -> None:
    if length > 1:
        py5.line(x, y, x + length, y)
        cantor(x, y + 20, length / 3)
        cantor(x + (2 * length) / 3, y + 20, length / 3)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "cantor_set_####.png"))


py5.run_sketch()
