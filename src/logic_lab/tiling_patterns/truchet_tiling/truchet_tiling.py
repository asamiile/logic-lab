from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

tiling: "TruchetTiling | None" = None


class TruchetTiling:
    def __init__(self, width=800, height=800, tile_size=40):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.cols = width // tile_size
        self.rows = height // tile_size
        self.grid = self._generate_grid()

    def _generate_grid(self):
        grid = []
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(np.random.choice([0, 1]))
            grid.append(row)
        return grid

    def draw_tile(self, x, y, rotation):
        """Draw a Truchet tile (quarter circle arc)"""
        py5.no_fill()
        py5.stroke(50)
        py5.stroke_weight(2)

        cx = x + self.tile_size / 2
        cy = y + self.tile_size / 2
        radius = self.tile_size / 2

        py5.push_matrix()
        py5.translate(cx, cy)
        py5.rotate(rotation)

        py5.arc(0, 0, self.tile_size, self.tile_size, 0, py5.PI / 2, py5.OPEN)

        py5.pop_matrix()

    def draw(self):
        py5.background(255)

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.tile_size
                y = row * self.tile_size
                rotation = self.grid[row][col] * py5.PI / 2
                self.draw_tile(x, y, rotation)


def setup() -> None:
    py5.size(800, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global tiling
    tiling = TruchetTiling(py5.width, py5.height, tile_size=40)


def draw() -> None:
    tiling.draw()
    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text("Truchet Tiling - Press SPACE to regenerate", 10, 20)


def key_pressed() -> None:
    if py5.key == " ":
        global tiling
        tiling = TruchetTiling(py5.width, py5.height, tile_size=40)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "truchet_tiling_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
