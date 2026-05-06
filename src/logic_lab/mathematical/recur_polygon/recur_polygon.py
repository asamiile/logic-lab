from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

gap = 0.1
gon = 8
vec: list[tuple[float, float]] = []


def setup() -> None:
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_vectors()
    py5.background(255)


def draw() -> None:
    global vec
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    draw_polygon(vec)
    py5.pop_matrix()
    vec = get_vector(vec)


def reset_vectors() -> None:
    global vec
    vec = []
    for i in range(gon):
        angle = 2 * i * py5.PI / gon
        vec.append((py5.cos(angle) * py5.width / 2, py5.sin(angle) * py5.width / 2))


def draw_polygon(points: list[tuple[float, float]]) -> None:
    for i in range(gon):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % gon]
        py5.line(x1, y1, x2, y2)


def get_vector(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    next_vec = []
    for i in range(gon):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % gon]
        next_vec.append((x1 + (x2 - x1) * gap, y1 + (y2 - y1) * gap))
    return next_vec


def mouse_clicked() -> None:
    global gap, gon
    gap = py5.random(1) / 2
    gon = int(py5.random(4, 16))
    py5.background(255)
    reset_vectors()
    print("gon =", gon, "gap =", gap)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "recur_polygon_####.png"))


py5.run_sketch()
