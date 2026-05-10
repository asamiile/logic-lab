import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
magnets = [(300, 200), (700, 200), (500, 600)]


def setup() -> None:
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_basin()


def draw_basin() -> None:
    py5.load_pixels()

    for py in range(py5.height):
        for px in range(py5.width):
            x, y = px * 0.01, py * 0.01
            vx, vy = 0.0, 0.0

            for _ in range(100):
                closest_magnet = -1
                min_dist = float("inf")

                fx, fy = 0, 0
                for i, (mx, my) in enumerate(magnets):
                    dx = x * 100 - mx
                    dy = y * 100 - my
                    dist = math.sqrt(dx * dx + dy * dy)

                    if dist < 0.1:
                        dist = 0.1

                    force = 100 / (dist * dist)
                    fx += force * dx / dist
                    fy += force * dy / dist

                    if dist < min_dist:
                        min_dist = dist
                        closest_magnet = i

                vx += fx * 0.0001
                vy += fy * 0.0001
                x += vx * 0.01
                y += vy * 0.01

            if closest_magnet >= 0:
                color_val = closest_magnet * 85
                col = py5.color(color_val, 150, 255 - color_val)
                py5.pixels[py * py5.width + px] = col

    py5.update_pixels()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "magnetic_pendulum_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
