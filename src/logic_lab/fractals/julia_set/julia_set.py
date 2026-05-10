import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
time_value = 0.0


def setup() -> None:
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value
    time_value += 0.005

    c_x = 0.3 * math.cos(time_value)
    c_y = 0.3 * math.sin(time_value)

    py5.load_pixels()
    for py in range(py5.height):
        for px in range(py5.width):
            x = (px - py5.width / 2) / (py5.width / 4)
            y = (py - py5.height / 2) / (py5.height / 4)

            zx, zy = x, y
            for i in range(100):
                if zx * zx + zy * zy > 4:
                    break
                zx, zy = zx * zx - zy * zy + c_x, 2 * zx * zy + c_y

            color_val = int((i / 100.0) * 255)
            col = py5.color(color_val, 150, 255 - color_val)
            py5.pixels[py * py5.width + px] = col

    py5.update_pixels()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "julia_set_####.png"))


py5.run_sketch()
