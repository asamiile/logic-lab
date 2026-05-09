"""Wave Function Collapse - Procedural generation via constraint satisfaction."""

import random
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

TILE_SIZE = 40
GRID_WIDTH = 16
GRID_HEIGHT = 12

# Simple tile definitions: each tile is a 3x3 pattern
TILES = {
    "empty": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    "cross": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    "corner": [[1, 1, 0], [1, 0, 0], [0, 0, 0]],
    "line": [[1, 1, 1], [0, 0, 0], [0, 0, 0]],
    "full": [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
}

TILE_COLORS = {
    "empty": (255, 255, 255),
    "cross": (100, 150, 255),
    "corner": (255, 150, 100),
    "line": (100, 255, 150),
    "full": (200, 100, 255),
}

# Adjacency rules: which tiles can be neighbors
ADJACENCY = {
    "empty": set(TILES.keys()),
    "cross": set(TILES.keys()),
    "corner": set(TILES.keys()),
    "line": set(TILES.keys()),
    "full": set(TILES.keys()),
}


@dataclass
class Cell:
    x: int
    y: int
    possibilities: set[str] = None
    tile: str = None

    def __post_init__(self):
        if self.possibilities is None:
            self.possibilities = set(TILES.keys())

    def is_determined(self) -> bool:
        return self.tile is not None

    def entropy(self) -> int:
        return len(self.possibilities)


class WFC:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
        self.finished = False

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

    def constrain(self):
        """Propagate constraints: remove impossible tiles based on neighbors."""
        changed = True
        while changed:
            changed = False
            for y in range(self.height):
                for x in range(self.width):
                    cell = self.grid[y][x]
                    if cell.is_determined():
                        continue

                    new_possibilities = set(cell.possibilities)
                    for nx, ny in self.get_neighbors(x, y):
                        neighbor = self.grid[ny][nx]
                        if neighbor.is_determined():
                            allowed = ADJACENCY[neighbor.tile]
                            new_possibilities &= allowed

                    if len(new_possibilities) < len(cell.possibilities):
                        cell.possibilities = new_possibilities
                        changed = True

                    if len(cell.possibilities) == 0:
                        return False
        return True

    def step(self) -> bool:
        """Collapse one cell and propagate constraints."""
        # Find undetermined cell with minimum entropy
        min_entropy = float("inf")
        min_cell = None
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if not cell.is_determined():
                    entropy = cell.entropy()
                    if entropy > 0 and entropy < min_entropy:
                        min_entropy = entropy
                        min_cell = cell

        if min_cell is None:
            # All cells determined
            return True

        # Collapse the cell
        min_cell.tile = random.choice(list(min_cell.possibilities))
        min_cell.possibilities = {min_cell.tile}

        # Propagate constraints
        return self.constrain()

    def collapse_all(self):
        """Collapse entire grid."""
        while not self.finished:
            if not self.step():
                self.reset()
                return
        self.finished = True

    def reset(self):
        """Reset the grid."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = Cell(x, y)
        self.finished = False


wfc = WFC(GRID_WIDTH, GRID_HEIGHT)
collapse_progress = 0


def setup() -> None:
    py5.size(TILE_SIZE * GRID_WIDTH, TILE_SIZE * GRID_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global collapse_progress

    py5.background(240)

    # Perform one step per frame
    if not wfc.finished:
        if not wfc.step():
            # Restart on contradiction
            wfc.reset()
        else:
            collapse_progress += 1

    # Draw grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = wfc.grid[y][x]
            if cell.is_determined():
                color = TILE_COLORS[cell.tile]
                py5.fill(*color)
                py5.no_stroke()
                py5.rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )

                # Draw tile pattern
                py5.stroke(0)
                py5.stroke_weight(0.5)
                pattern = TILES[cell.tile]
                cell_size = TILE_SIZE // 3
                for py_idx, row in enumerate(pattern):
                    for px_idx, pixel in enumerate(row):
                        if pixel:
                            px = x * TILE_SIZE + px_idx * cell_size
                            py_pos = y * TILE_SIZE + py_idx * cell_size
                            py5.line(px, py_pos, px + cell_size, py_pos + cell_size)
            else:
                # Undetermined cell
                py5.no_fill()
                py5.stroke(200)
                py5.stroke_weight(1)
                py5.rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )

    # Info
    py5.fill(0)
    py5.text_size(12)
    py5.text(
        f"WFC | Collapsed: {collapse_progress}/{GRID_WIDTH * GRID_HEIGHT}",
        10,
        py5.height - 10,
    )


def key_pressed() -> None:
    global wfc, collapse_progress
    if py5.key == " ":
        wfc.reset()
        collapse_progress = 0
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "wave_function_collapse_####.png"))


py5.run_sketch()
