from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
MOD = 5


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_table()
    py5.no_loop()


def draw_table() -> None:
    scalar = py5.width / MOD
    py5.background(255)
    py5.stroke(0)

    for i in range(MOD):
        for j in range(MOD):
            num = (i + j) % MOD
            x_pos = j * scalar
            y_pos = i * scalar
            py5.fill(255)
            py5.rect(x_pos, y_pos, scalar, scalar)
            py5.fill(0)
            py5.text_size(scalar)
            py5.text(str(num), x_pos, y_pos + scalar)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "modular_table_####.png"))


py5.run_sketch()

