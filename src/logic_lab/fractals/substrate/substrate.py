from dataclasses import dataclass
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
substrate: "SubstrateCracks | None" = None


@dataclass
class Crack:
    x: float
    y: float
    dx: float
    dy: float
    length: float = 0


class SubstrateCracks:
    def __init__(self, width: float = 800, height: float = 800) -> None:
        self.width = width
        self.height = height
        self.cracks: list[Crack] = []
        self.visited: set = set()

        start_x = width / 2
        start_y = height / 2
        angle = np.random.uniform(0, 2 * np.pi)
        self.cracks.append(Crack(start_x, start_y, float(np.cos(angle)), float(np.sin(angle))))

    def get_neighbors(self, x: float, y: float, cell_size: int = 5) -> list[Crack]:
        neighbors: list[Crack] = []
        grid_x = int(x / cell_size)
        grid_y = int(y / cell_size)

        for crack in self.cracks[-100:]:
            cx = int(crack.x / cell_size)
            cy = int(crack.y / cell_size)
            if abs(cx - grid_x) <= 2 and abs(cy - grid_y) <= 2:
                neighbors.append(crack)

        return neighbors

    def propagate(self) -> None:
        if len(self.cracks) > 2000:
            return

        idx = int(np.random.randint(max(0, len(self.cracks) - 100), len(self.cracks)))
        crack = self.cracks[idx]

        neighbors = self.get_neighbors(crack.x, crack.y)

        angle = float(np.arctan2(crack.dy, crack.dx))

        perpendicular_angle = angle + np.pi / 2
        if np.random.random() < 0.5:
            perpendicular_angle = angle - np.pi / 2

        new_angle = angle + float(np.random.normal(0, 0.3))

        new_x = crack.x + float(np.cos(new_angle)) * 3
        new_y = crack.y + float(np.sin(new_angle)) * 3

        if 0 < new_x < self.width and 0 < new_y < self.height:
            new_crack = Crack(new_x, new_y, float(np.cos(new_angle)), float(np.sin(new_angle)))
            self.cracks.append(new_crack)

    def draw(self) -> None:
        py5.background(240)

        py5.stroke(100)
        py5.stroke_weight(1)

        for i in range(1, len(self.cracks)):
            prev = self.cracks[i - 1]
            curr = self.cracks[i]
            py5.line(prev.x, prev.y, curr.x, curr.y)

        py5.fill(50, 50, 150, 100)
        py5.no_stroke()
        py5.circle(self.cracks[0].x, self.cracks[0].y, 5)


def setup() -> None:
    global substrate
    py5.size(800, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    substrate = SubstrateCracks(py5.width, py5.height)


def draw() -> None:
    for _ in range(5):
        substrate.propagate()

    substrate.draw()

    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text(f"Cracks: {len(substrate.cracks)}", 10, 20)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "substrate_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
