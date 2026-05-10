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

    size = 100
    field = [
        [random.random() * 0.5 if random.random() < 0.1 else 0 for _ in range(size)]
        for _ in range(size)
    ]


def kernel_step(value: float) -> float:
    if value < 0.3:
        return 0.0
    elif value < 0.5:
        return 1.0
    else:
        return 0.5


def draw() -> None:
    global field
    new_field = [[0.0] * len(field[0]) for _ in range(len(field))]

    for y in range(len(field)):
        for x in range(len(field[0])):
            neighbors = 0.0
            count = 0

            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if dx == 0 and dy == 0:
                        continue
                    ny = (y + dy) % len(field)
                    nx = (x + dx) % len(field[0])

                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= 3:
                        neighbors += field[ny][nx] / (1 + dist)
                        count += 1

            if count > 0:
                neighbors /= count

            step_val = kernel_step(neighbors)
            new_field[y][x] = max(0, min(1.0, field[y][x] + (step_val - 0.5) * 0.1))

    field = new_field

    py5.background(20)
    cell_size = py5.width // len(field)

    for y in range(len(field)):
        for x in range(len(field[0])):
            val = int(field[y][x] * 255)
            py5.fill(val, 200, 255 - val)
            py5.stroke_weight(0)
            py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lenia_####.png"))


py5.run_sketch()
