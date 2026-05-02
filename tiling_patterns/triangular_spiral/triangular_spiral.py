from pathlib import Path
from math import pi
import sys

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.aperiodic_helpers import initial_triangle


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
tri = None
rad_end = 7 * pi / 5


def setup() -> None:
    global tri
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    tri = initial_triangle(200)
    py5.background(255)
    golden_division()
    py5.no_loop()


def golden_division() -> None:
    global rad_end
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.fill(255)
    py5.stroke(0)
    tri.draw_triangle()
    tri.update_thin_s()
    rad_end = tri.draw_arc(rad_end)
    py5.pop_matrix()


def mouse_clicked() -> None:
    golden_division()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "triangular_spiral_####.png"))


py5.run_sketch()
