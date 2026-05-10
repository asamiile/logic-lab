import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
grid: list[list[int]] = []


def setup() -> None:
    global grid
    py5.size(800, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    grid = [[0] * 80 for _ in range(100)]


def draw() -> None:
    global grid

    if random.random() < 0.3:
        grid[0][random.randint(0, 79)] = 1

    for y in range(len(grid) - 2, -1, -1):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                if grid[y + 1][x] == 0:
                    grid[y + 1][x] = 1
                    grid[y][x] = 0
                elif x > 0 and grid[y + 1][x - 1] == 0:
                    grid[y + 1][x - 1] = 1
                    grid[y][x] = 0
                elif x < len(grid[0]) - 1 and grid[y + 1][x + 1] == 0:
                    grid[y + 1][x + 1] = 1
                    grid[y][x] = 0

    py5.background(20)
    cell_size = py5.width // len(grid[0])

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                py5.fill(200, 150, 100)
                py5.stroke_weight(0)
                py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "sand_simulation_####.png"))


py5.run_sketch()
