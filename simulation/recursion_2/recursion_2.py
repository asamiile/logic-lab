from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    draw_circles(py5.width / 2, py5.height / 2, 320)
    py5.no_loop()


def draw_circles(x: float, y: float, radius: float) -> None:
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.no_fill()
    py5.circle(x, y, radius * 2)
    if radius > 4:
        draw_circles(x + radius / 2, y, radius / 2)
        draw_circles(x - radius / 2, y, radius / 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recursion_2_####.png"))


py5.run_sketch()
