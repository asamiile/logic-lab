from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 600)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_recaman()


def draw_recaman() -> None:
    py5.stroke_weight(2)
    py5.no_fill()

    visited = set()
    x, y = py5.width / 2, py5.height / 2
    n = 1

    for i in range(500):
        backward = x - n
        if backward >= 0 and backward not in visited:
            x = backward
        else:
            x = x + n

        color_val = i % 256
        py5.stroke(color_val, 255 - color_val, 128)
        py5.arc(
            x, y, abs(x - (py5.width / 2)) * 2, abs(x - (py5.width / 2)) * 2, 0, py5.PI, py5.OPEN
        )

        visited.add(x)
        n += 1


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recaman_sequence_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
