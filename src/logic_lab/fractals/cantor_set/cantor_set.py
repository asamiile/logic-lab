from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 600)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_cantor()


def draw_cantor() -> None:
    py5.stroke_weight(2)

    def draw_line(x: float, y: float, length: float, depth: int) -> None:
        if depth == 0 or length < 1:
            py5.stroke(100 + depth * 20, 200, 100)
            py5.line(x, y, x + length, y)
            return

        third = length / 3
        draw_line(x, y + 20 * depth, third, depth - 1)
        draw_line(x + 2 * third, y + 20 * depth, third, depth - 1)

    draw_line(100, 50, py5.width - 200, 8)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "cantor_set_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
