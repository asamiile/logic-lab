import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
field: list[list[float]] = []


def setup() -> None:
    global field
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    size = 50
    field = [[random.random() for _ in range(size)] for _ in range(size)]


def draw() -> None:
    global field
    new_field = [[0.0] * len(field[0]) for _ in range(len(field))]

    for y in range(len(field)):
        for x in range(len(field[0])):
            neighbors = 0.0

            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    dist = math.sqrt(dx * dx + dy * dy)
                    if 0 < dist <= 2.5:
                        ny = (y + dy) % len(field)
                        nx = (x + dx) % len(field[0])
                        neighbors += field[ny][nx] / (1 + dist)

            current = field[y][x]
            neighbors /= 5.0

            if 0.3 < neighbors < 0.8:
                new_field[y][x] = min(1.0, current + 0.1)
            elif neighbors > 0.5:
                new_field[y][x] = max(0.0, current - 0.05)
            else:
                new_field[y][x] = current * 0.95

    field = new_field

    py5.background(20)
    cell_size = py5.width // len(field)

    for y in range(len(field)):
        for x in range(len(field[0])):
            val = int(field[y][x] * 255)
            py5.fill(val, 200 - val, 255 - val)
            py5.stroke_weight(0)
            py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "smooth_life_####.png"))


py5.run_sketch()
