from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

theta = 0.0
STEP = 2 * py5.PI * 0.01


def setup() -> None:
    py5.size(500, 500)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global theta
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.line(
        rad(theta) * py5.cos(theta),
        rad(theta) * py5.sin(theta),
        rad(theta + STEP) * py5.cos(theta + STEP),
        rad(theta + STEP) * py5.sin(theta + STEP),
    )
    py5.pop_matrix()
    theta += STEP


def rad(t: float) -> float:
    return 5 * t


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "log_spiral_####.png"))


py5.run_sketch()

