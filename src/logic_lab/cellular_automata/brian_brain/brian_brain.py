import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
grid: list[list[int]] = []


def setup() -> None:
    global grid
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    size = 100
    grid = [
        [random.choice([0, 1]) if random.random() < 0.3 else 0 for _ in range(size)]
        for _ in range(size)
    ]


def draw() -> None:
    global grid
    new_grid = [[0] * len(grid[0]) for _ in range(len(grid))]

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            neighbors = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % len(grid)
                    nx = (x + dx) % len(grid[0])
                    if grid[ny][nx] == 1:
                        neighbors += 1

            if grid[y][x] == 1:
                new_grid[y][x] = 2
            elif grid[y][x] == 2:
                new_grid[y][x] = 0
            elif neighbors == 2:
                new_grid[y][x] = 1

    grid = new_grid

    py5.background(20)
    cell_size = py5.width // len(grid)

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                py5.fill(255, 100, 100)
            elif grid[y][x] == 2:
                py5.fill(100, 255, 100)
            else:
                continue

            py5.stroke_weight(0)
            py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "brian_brain_####.png"))


py5.run_sketch()
