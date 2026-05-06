from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def draw_lines(x1: float, y1: float, x2: float, y2: float) -> None:
    py5.line(x1, y1, x2, y2)

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy > 4:
        draw_lines(x1 - dy / 3, y1, x1 + dy / 3, y1)
        draw_lines(x1 - dy / 3, y2, x1 + dy / 3, y2)
    elif dy == 0 and dx > 4:
        draw_lines(x1, y1 - dx / 3, x1, y1 + dx / 3)
        draw_lines(x2, y1 - dx / 3, x2, y1 + dx / 3)


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    draw_lines(py5.width / 4, py5.height / 2, (3 * py5.width) / 4, py5.height / 2)
    py5.no_loop()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fractal_lines_####.png"))


py5.run_sketch()
