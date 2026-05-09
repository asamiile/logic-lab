from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

COLS = 144
ROWS = 84
DAMPING = 0.992

current = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]
previous = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]
cell_w = 1.0
cell_h = 1.0


def setup() -> None:
    global cell_w, cell_h
    py5.size(720, 420)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    cell_w = py5.width / COLS
    cell_h = py5.height / ROWS
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    disturb(COLS // 2, ROWS // 2, 620)


def disturb(cx: int, cy: int, strength: float) -> None:
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x = cx + dx
            y = cy + dy
            if 1 <= x < COLS - 1 and 1 <= y < ROWS - 1:
                current[y][x] += strength / (1 + dx * dx + dy * dy)


def step_wave() -> None:
    global current, previous
    next_grid = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(1, ROWS - 1):
        for x in range(1, COLS - 1):
            value = (
                current[y - 1][x] + current[y + 1][x] + current[y][x - 1] + current[y][x + 1]
            ) * 0.5 - previous[y][x]
            next_grid[y][x] = value * DAMPING
    previous = current
    current = next_grid


def draw() -> None:
    step_wave()
    if py5.frame_count % 140 == 0:
        disturb(int(py5.random(18, COLS - 18)), int(py5.random(14, ROWS - 14)), 520)

    py5.background(215, 30, 8)
    py5.no_stroke()
    for y in range(ROWS):
        for x in range(COLS):
            value = py5.constrain(current[y][x] * 0.018, -1, 1)
            py5.fill(202 + value * 42, 62, 42 + abs(value) * 55, 92)
            py5.rect(x * cell_w, y * cell_h, cell_w + 1, cell_h + 1)


def mouse_dragged() -> None:
    disturb(int(py5.mouse_x / cell_w), int(py5.mouse_y / cell_h), 480)


def mouse_pressed() -> None:
    disturb(int(py5.mouse_x / cell_w), int(py5.mouse_y / cell_h), 620)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "wave_equation_grid_####.png"))


py5.run_sketch()
