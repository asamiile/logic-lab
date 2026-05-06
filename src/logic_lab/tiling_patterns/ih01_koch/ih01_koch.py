import sys
from pathlib import Path

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.deformation_helpers import (
    draw_poly,
    draw_tiling,
    hex_lattice,
    hex_vertices,
    koch_points,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 10
scalar = 0.0
upper_limit = 0
lattice = []


def setup() -> None:
    global scalar, lattice
    py5.size(500, 500, py5.P2D)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    lattice = hex_lattice(NUM, scalar, py5.height)
    draw_current()
    py5.no_loop()


def tile_points() -> list[tuple[float, float]]:
    vertices = hex_vertices(scalar)
    points = []
    for i in range(6):
        segment = koch_points(vertices[i], vertices[(i + 1) % 6], upper_limit, i < 3)
        points.extend(segment if not points else segment[1:])
    return points


def draw_current() -> None:
    py5.background(1, 0, 1)
    points = tile_points()
    draw_tiling(lattice, lambda _i, _j: draw_poly(points, py5.color(py5.random(1), 1, 1)))


def mouse_clicked() -> None:
    global upper_limit
    upper_limit += 1
    draw_current()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ih01_koch_####.png"))


py5.run_sketch()
