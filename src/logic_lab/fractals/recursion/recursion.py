from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    draw_circles(py5.width / 2, py5.height / 2, py5.width / 2)
    py5.no_loop()


def draw_circles(x: float, y: float, r: float) -> None:
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.circle(x, y, r * 2)
    if r > 4:
        draw_circles(x, y, r * 0.75)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recursion_####.png"))


py5.run_sketch()
