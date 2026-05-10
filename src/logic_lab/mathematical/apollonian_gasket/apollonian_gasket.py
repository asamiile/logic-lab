import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    py5.size(1000, 1000)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    generate_gasket()


def generate_gasket() -> None:
    py5.stroke_weight(1)
    py5.stroke(150, 200, 255)
    py5.no_fill()

    center_x, center_y = py5.width / 2, py5.height / 2
    outer_radius = 400

    circles = [{"x": center_x, "y": center_y, "r": outer_radius}]

    for level in range(6):
        new_circles = []
        for circle in circles[-30:]:
            cx, cy, cr = circle["x"], circle["y"], circle["r"]

            for angle in [0, 120, 240]:
                rad = math.radians(angle)
                new_r = cr / 3.0
                new_x = cx + (cr - new_r) * math.cos(rad)
                new_y = cy + (cr - new_r) * math.sin(rad)

                new_circles.append({"x": new_x, "y": new_y, "r": new_r})

        circles.extend(new_circles)

    for circle in circles:
        py5.circle(circle["x"], circle["y"], circle["r"] * 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "apollonian_gasket_####.png"))


py5.run_sketch()
