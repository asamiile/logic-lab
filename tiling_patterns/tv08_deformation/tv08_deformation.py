from pathlib import Path
from math import sqrt
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.deformation_helpers import deformed_hex_lattice, draw_poly, draw_tiling, tv08_vertices


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
ROW = 10
scalar = 0.0
hor = 0.0
ver = 0.0
lattice = []
tile_colors = []


def setup() -> None:
    global scalar
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / ROW
    randomize_colors()


def draw() -> None:
    global lattice
    py5.background(1, 0, 1)
    lattice = deformed_hex_lattice(ROW, scalar, py5.height, hor)
    vertices = tv08_vertices(scalar, hor, ver)
    draw_tiling(lattice, lambda i, j: draw_poly(vertices, tile_colors[i][j]), True)
    draw_status()


def draw_status() -> None:
    py5.fill(0)
    py5.no_stroke()
    py5.rect(0, 0, 190, 42)
    py5.fill(0, 0, 1)
    py5.text_size(12)
    py5.text(f"hor {hor:.2f}  ver {ver:.2f}", 10, 18)
    py5.text("A/Z hor  S/X ver  R colors", 10, 36)


def randomize_colors() -> None:
    global tile_colors
    sample = deformed_hex_lattice(ROW, scalar or 50, 500, hor)
    tile_colors = [[py5.color(py5.random(1), 1, 1) for _ in row] for row in sample]


def key_pressed() -> None:
    global hor, ver
    key = str(py5.key).lower()
    if key == "a":
        hor = min((sqrt(3) - 1) / 2, hor + 0.05)
    elif key == "z":
        hor = max(-1, hor - 0.05)
    elif key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "tv08_deformation_####.png"))
    elif key == "x":
        ver = max(0, ver - 0.05)
    elif key == "r":
        randomize_colors()
    elif key == "d":
        ver = min(1, ver + 0.05)


py5.run_sketch()
