from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_burning_ship()


def draw_burning_ship() -> None:
    py5.load_pixels()
    max_iterations = 100

    for py in range(py5.height):
        for px in range(py5.width):
            x = (px - py5.width * 0.6) / (py5.width * 0.3)
            y = (py - py5.height / 2) / (py5.height * 0.3)

            cx, cy = x, y
            iterations = 0

            while iterations < max_iterations and cx * cx + cy * cy < 4:
                cx = abs(cx * cx - cy * cy + x)
                cy = abs(2 * cx * cy + y)
                iterations += 1

            hue = (iterations / max_iterations) * 255
            py5.pixels[py * py5.width + px] = py5.color(hue, 100, 255 - hue)

    py5.update_pixels()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "burning_ship_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
