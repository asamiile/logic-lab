from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

COLS = 150
ROWS = 96
RESTING = 0
EXCITED = 1
REFRACTORY = 2

state = [[RESTING for _ in range(COLS)] for _ in range(ROWS)]
timer = [[0 for _ in range(COLS)] for _ in range(ROWS)]
cell_w = 1.0
cell_h = 1.0


def setup() -> None:
    global cell_w, cell_h
    py5.size(750, 480)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    cell_w = py5.width / COLS
    cell_h = py5.height / ROWS
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    excite(COLS // 2, ROWS // 2, 8)


def excite(cx: int, cy: int, radius: int) -> None:
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if 0 <= x < COLS and 0 <= y < ROWS and (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius:
                state[y][x] = EXCITED
                timer[y][x] = 5


def excited_neighbors(x: int, y: int) -> int:
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and state[ny][nx] == EXCITED:
                count += 1
    return count


def step_medium() -> None:
    new_state = [row[:] for row in state]
    new_timer = [row[:] for row in timer]
    for y in range(ROWS):
        for x in range(COLS):
            if state[y][x] == RESTING:
                if excited_neighbors(x, y) >= 2:
                    new_state[y][x] = EXCITED
                    new_timer[y][x] = 5
            elif state[y][x] == EXCITED:
                new_timer[y][x] -= 1
                if new_timer[y][x] <= 0:
                    new_state[y][x] = REFRACTORY
                    new_timer[y][x] = 16
            else:
                new_timer[y][x] -= 1
                if new_timer[y][x] <= 0:
                    new_state[y][x] = RESTING
                    new_timer[y][x] = 0
    for y in range(ROWS):
        state[y] = new_state[y]
        timer[y] = new_timer[y]


def draw() -> None:
    if py5.frame_count % 3 == 0:
        step_medium()
    if py5.frame_count % 180 == 0:
        excite(int(py5.random(20, COLS - 20)), int(py5.random(16, ROWS - 16)), 5)

    py5.no_stroke()
    for y in range(ROWS):
        for x in range(COLS):
            if state[y][x] == EXCITED:
                py5.fill(32, 86, 98, 96)
            elif state[y][x] == REFRACTORY:
                py5.fill(300, 50, 28 + timer[y][x] * 2, 90)
            else:
                py5.fill(214, 20, 8, 100)
            py5.rect(x * cell_w, y * cell_h, cell_w + 1, cell_h + 1)


def mouse_pressed() -> None:
    excite(int(py5.mouse_x / cell_w), int(py5.mouse_y / cell_h), 7)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "excitable_wavefronts_####.png"))


py5.run_sketch()
