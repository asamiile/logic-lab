from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
MOD = 37


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_power_table()
    py5.no_loop()


def draw_power_table() -> None:
    scalar = py5.width / (MOD - 1)
    py5.background(0, 0, 1)

    for i in range(1, MOD):
        num = i
        for j in range(1, MOD):
            x_pos = (j - 0.5) * scalar
            y_pos = (i - 0.5) * scalar
            py5.no_stroke()
            py5.fill(num / MOD, 1, 1)
            py5.ellipse(x_pos, y_pos, scalar / 2, scalar / 2)
            py5.fill(0, 0, 0)
            py5.ellipse(x_pos, y_pos, scalar * num / MOD, scalar * num / MOD)
            num = (num * i) % MOD


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "modular_power_visual_####.png"))


py5.run_sketch()

