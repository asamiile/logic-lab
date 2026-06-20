"""
Conway's Game of Life (and variants)
Each cell is alive or dead. Every generation:
  Birth:   dead cell with exactly B neighbor counts becomes alive.
  Survive: live cell with S neighbor counts stays alive; otherwise dies.

Conway's original rule B3/S23 produces the classic Game of Life behavior:
gliders, oscillators, spaceships, and complex emergent patterns.

Age coloring: a cell's color reflects how many generations it has been
continuously alive — young cells glow hot (yellow/white), old cells cool
to blue/teal. Newly born cells flash bright.

Rule presets:
  1  Conway     B3/S23        — classic
  2  HighLife   B36/S23       — supports replicators
  3  Day&Night  B3678/S34678  — symmetric, intricate
  4  Maze       B3/S12345     — organic labyrinthine mazes
  5  Seeds      B2/S          — everything dies after one step → chaotic sparks

Controls:
  1-5     — switch rule
  r       — randomize grid
  Space   — pause / resume
  c       — step one generation (while paused)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
CELL = 2  # pixel size of each cell
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
MAX_AGE = 60  # age at which color saturates to "old"

RULES = {
    "conway": ([3], [2, 3]),
    "highlife": ([3, 6], [2, 3]),
    "day_night": ([3, 6, 7, 8], [3, 4, 6, 7, 8]),
    "maze": ([3], [1, 2, 3, 4, 5]),
    "seeds": ([2], []),
}
RULE_NAMES = list(RULES.keys())
rule_idx = 0
paused = False

_grid: np.ndarray  # (ROWS, COLS) bool — alive
_age: np.ndarray  # (ROWS, COLS) int  — consecutive alive generations


def _reset() -> None:
    global _grid, _age
    _grid = (np.random.random((ROWS, COLS)) < 0.30).astype(np.int8)
    _age = np.zeros((ROWS, COLS), dtype=np.int32)


def _step() -> None:
    global _grid, _age
    birth_counts, survive_counts = RULES[RULE_NAMES[rule_idx]]

    # Count live neighbours via 8-directional roll sum
    nbr = (
        np.roll(_grid, -1, 0)
        + np.roll(_grid, 1, 0)
        + np.roll(_grid, -1, 1)
        + np.roll(_grid, 1, 1)
        + np.roll(np.roll(_grid, -1, 0), -1, 1)
        + np.roll(np.roll(_grid, -1, 0), 1, 1)
        + np.roll(np.roll(_grid, 1, 0), -1, 1)
        + np.roll(np.roll(_grid, 1, 0), 1, 1)
    )

    born = (_grid == 0) & np.isin(nbr, birth_counts)
    survive = (_grid == 1) & np.isin(nbr, survive_counts)
    new_grid = (born | survive).astype(np.int8)

    # Update age: increment survivors, reset newly born
    _age = np.where(new_grid & _grid, np.minimum(_age + 1, MAX_AGE), 0)
    _age = np.where(born, 1, _age)
    _grid = new_grid


def _render() -> None:
    ph, pw = py5.pixel_height, py5.pixel_width
    ry = (np.arange(ph) * ROWS / ph).astype(int).clip(0, ROWS - 1)
    rx = (np.arange(pw) * COLS / pw).astype(int).clip(0, COLS - 1)

    alive_d = _grid[np.ix_(ry, rx)].astype(bool)
    age_d = _age[np.ix_(ry, rx)].astype(np.float32)
    t = np.clip(age_d / MAX_AGE, 0, 1)

    # Color:  newborn  = bright yellow-white
    #         young    = orange
    #         middle   = green
    #         old      = teal/blue
    r8 = np.where(alive_d, np.clip((1.0 - t * 0.7) * 255, 0, 255), 8).astype(np.uint8)
    g8 = np.where(alive_d, np.clip((0.9 - t * 0.3) * 255, 0, 255), 10).astype(np.uint8)
    b8 = np.where(alive_d, np.clip(t * 255 + (1 - t) * 20, 0, 255), 14).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(30)
    _reset()


def draw() -> None:
    if not paused:
        _step()
    _render()

    alive_count = int(_grid.sum())
    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Game of Life  rule:{RULE_NAMES[rule_idx]}  "
        f"alive:{alive_count}  gen:{py5.frame_count}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global rule_idx, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "c" and paused:
        _step()
    elif k == "1":
        rule_idx = 0
        _reset()
    elif k == "2":
        rule_idx = 1
        _reset()
    elif k == "3":
        rule_idx = 2
        _reset()
    elif k == "4":
        rule_idx = 3
        _reset()
    elif k == "5":
        rule_idx = 4
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"life_{RULE_NAMES[rule_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
