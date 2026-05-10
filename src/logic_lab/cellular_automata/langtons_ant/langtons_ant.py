from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
ant_x: int = 0 if "int" == "int" else 0.0
grid: list[list[int]] = []
ant_x, ant_y = 0, 0
ant_dir = 0


def setup() -> None:
    global grid, ant_x, ant_y
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    size = 100
    grid = [[0] * size for _ in range(size)]
    ant_x, ant_y = size // 2, size // 2


def draw() -> None:
    global ant_x, ant_y, ant_dir

    cell_size = py5.width // len(grid)

    for _ in range(100):
        current = grid[ant_y][ant_x]

        if current == 0:
            ant_dir = (ant_dir - 1) % 4
            grid[ant_y][ant_x] = 1
        else:
            ant_dir = (ant_dir + 1) % 4
            grid[ant_y][ant_x] = 0

        if ant_dir == 0:
            ant_y = (ant_y - 1) % len(grid)
        elif ant_dir == 1:
            ant_x = (ant_x + 1) % len(grid[0])
        elif ant_dir == 2:
            ant_y = (ant_y + 1) % len(grid)
        else:
            ant_x = (ant_x - 1) % len(grid[0])

    py5.background(20)
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                py5.fill(100, 200, 255)
                py5.stroke_weight(0)
                py5.rect(x * cell_size, y * cell_size, cell_size, cell_size)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "langtons_ant_####.png"))


py5.run_sketch()
