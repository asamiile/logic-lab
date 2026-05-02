from pathlib import Path
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.aperiodic_helpers import Tri, initial_triangle


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
thin: list[Tri] = []
fat: list[Tri] = []
colors = []
generation = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    initialize(1200)
    triangular_division()
    py5.no_loop()


def initialize(scalar: float) -> None:
    global thin, fat, colors, generation
    colors = [py5.color(py5.random(1), 1, 1), py5.color(py5.random(1), 1, 1)]
    thin = [initial_triangle(scalar)]
    fat = []
    generation = 0


def triangular_division() -> None:
    global thin, fat, generation
    next_thin: list[Tri] = []
    next_fat: list[Tri] = []
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.no_stroke()
    py5.fill(colors[0])
    for tri in thin:
        tri.draw_triangle()
        tri.div_thin_s(next_thin, next_fat)
    py5.fill(colors[1])
    for tri in fat:
        tri.draw_triangle()
        tri.div_fat_l(next_thin, next_fat)
    py5.pop_matrix()
    thin = next_thin
    fat = next_fat
    generation += 1


def mouse_clicked() -> None:
    triangular_division()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recur_triangle_####.png"))
    elif str(py5.key).lower() == "r":
        py5.background(255)
        initialize(1200)
        triangular_division()


py5.run_sketch()
