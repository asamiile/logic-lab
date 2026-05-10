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
    grid = [[random.randint(0, 5) for _ in range(size)] for _ in range(size)]


def draw() -> None:
    global grid
    new_grid = [row[:] for row in grid]
    threshold = 1

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            current = grid[y][x]
            next_state = (current + 1) % 6
            count = 0

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % len(grid)
                    nx = (x + dx) % len(grid[0])
                    if grid[ny][nx] == next_state:
                        count += 1

            if count >= threshold:
                new_grid[y][x] = next_state

    grid = new_grid

    py5.background(20)
    cell_size = py5.width // len(grid)
    colors = [
        (255, 100, 100),
        (100, 255, 100),
        (100, 100, 255),
        (255, 255, 100),
        (255, 100, 255),
        (100, 255, 255),
    ]

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            py5.fill(*colors[grid[y][x]])
            py5.stroke_weight(0)
            py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "cyclic_ca_####.png"))


py5.run_sketch()
