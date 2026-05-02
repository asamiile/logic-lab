from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

gap = 0.01
vec: list[tuple[float, float]] = []


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_vectors()
    py5.background(255)


def draw() -> None:
    global vec
    draw_square(vec)
    vec = get_vector(vec)


def reset_vectors() -> None:
    global vec
    vec = [
        (0, 0),
        (py5.width, 0),
        (py5.width, py5.height),
        (0, py5.height),
    ]


def draw_square(points: list[tuple[float, float]]) -> None:
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        py5.line(x1, y1, x2, y2)


def get_vector(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    next_vec = []
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        next_vec.append((x1 + (x2 - x1) * gap, y1 + (y2 - y1) * gap))
    return next_vec


def mouse_clicked() -> None:
    global gap
    py5.background(255)
    gap = py5.random(1) / 2
    print("gap =", gap)
    reset_vectors()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recur_square_####.png"))


py5.run_sketch()

