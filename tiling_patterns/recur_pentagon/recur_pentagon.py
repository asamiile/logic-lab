from pathlib import Path
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.aperiodic_helpers import Pent


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
pents: list[Pent] = []
pent_color = None
generation = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    initialize(250)
    slit_division()
    py5.no_loop()


def initialize(scalar: float) -> None:
    global pents, pent_color, generation
    pent_color = py5.color(py5.random(1), 1, 1)
    pents = [Pent.from_center_vertex((0.0, 0.0), (scalar, 0.0))]
    generation = 0


def slit_division() -> None:
    global pents, generation
    next_pents = []
    py5.background(0, 0, 1)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.fill(pent_color)
    py5.stroke(0, 0, 0, 0.35)
    for pent in pents:
        pent.draw()
        pent.divide(next_pents)
    py5.pop_matrix()
    pents = next_pents
    generation += 1


def mouse_clicked() -> None:
    slit_division()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recur_pentagon_####.png"))
    elif str(py5.key).lower() == "r":
        initialize(250)
        slit_division()


py5.run_sketch()
