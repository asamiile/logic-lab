from pathlib import Path
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.aperiodic_helpers import Tri, initial_triangle


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
thin: list[Tri] = []
fat: list[Tri] = []
colors = []
mode = "pent"
generation = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    initialize(1200)
    divide_once()
    py5.no_loop()


def initialize(scalar: float) -> None:
    global thin, fat, colors, generation
    colors = [py5.color(py5.random(1), 1, 1), py5.color(py5.random(1), 1, 1)]
    thin = [initial_triangle(scalar)]
    fat = []
    generation = 0


def divide_once() -> None:
    if mode == "rhomb":
        rhomb_division()
    elif mode == "kite":
        kite_dart_division()
    else:
        pent_division()


def rhomb_division() -> None:
    global thin, fat, generation
    next_thin: list[Tri] = []
    next_fat: list[Tri] = []
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.fill(colors[0])
    for tri in thin:
        tri.draw_rhomb()
        tri.div_thin_s(next_thin, next_fat)
    py5.fill(colors[1])
    for tri in fat:
        tri.draw_rhomb()
        tri.div_fat_l(next_thin, next_fat)
    py5.pop_matrix()
    thin = next_thin
    fat = next_fat
    generation += 1


def kite_dart_division() -> None:
    global thin, fat, generation
    next_thin: list[Tri] = []
    next_fat: list[Tri] = []
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.fill(colors[0])
    for tri in thin:
        tri.draw_kite_dart()
        tri.div_thin_l(next_thin, next_fat)
    py5.fill(colors[1])
    for tri in fat:
        tri.draw_kite_dart()
        tri.div_fat_s(next_thin, next_fat)
    py5.pop_matrix()
    thin = next_thin
    fat = next_fat
    generation += 1


def pent_division() -> None:
    global thin, fat, generation
    next_thin: list[Tri] = []
    next_fat: list[Tri] = []
    py5.background(1, 0, 1)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    for tri in thin:
        tri.draw_pent_t(colors[0], colors[1])
        tri.div_thin_s(next_thin, next_fat)
    for tri in fat:
        tri.draw_pent_f(colors[0], colors[1])
        tri.div_fat_l(next_thin, next_fat)
    py5.pop_matrix()
    thin = next_thin
    fat = next_fat
    generation += 1


def reset_current_mode() -> None:
    initialize(1200)
    py5.background(255)
    divide_once()


def mouse_clicked() -> None:
    divide_once()


def key_pressed() -> None:
    global mode
    key = str(py5.key).lower()
    if key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "penrose_tiling_####.png"))
    elif key == "r":
        reset_current_mode()
    elif key == "1":
        mode = "pent"
        reset_current_mode()
    elif key == "2":
        mode = "rhomb"
        reset_current_mode()
    elif key == "3":
        mode = "kite"
        reset_current_mode()


py5.run_sketch()
