from pathlib import Path
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.deformation_helpers import draw_bezier_poly, draw_tiling, square_lattice, square_vertices


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 10
scalar = 0.0
lattice = []


def setup() -> None:
    global scalar, lattice
    py5.size(500, 500, py5.P2D)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    lattice = square_lattice(NUM, scalar)
    draw_current()
    py5.no_loop()


def draw_current() -> None:
    py5.background(1, 0, 1)
    vertices = square_vertices(scalar)
    draw_tiling(lattice, lambda _i, _j: draw_bezier_poly(vertices, "ih41", py5.color(py5.random(1), 1, 1)))


def mouse_clicked() -> None:
    draw_current()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ih41_deformation_####.png"))


py5.run_sketch()
