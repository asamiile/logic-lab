import sys
from math import atan, cos, pi, sin, sqrt
from pathlib import Path

import py5

sys.path.append(str(Path(__file__).resolve().parents[2]))
from tiling_patterns.pattern_helpers import add, from_angle, rotate, square_lattice, sub

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
NUM = 10
scalar = 0.0
lattice = []
gap = 0.5
colors = []
dirty = True


def setup() -> None:
    global scalar, lattice, colors
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height / NUM
    lattice = square_lattice(NUM, scalar)
    colors = [py5.color(py5.random(1), 0.4, 1) for _ in range(2)]


def draw() -> None:
    global dirty
    if py5.is_mouse_pressed:
        set_gap(py5.constrain(py5.mouse_x / py5.width, 0, 1))
    if not dirty:
        return
    draw_tiling()
    dirty = False


def set_gap(value: float) -> None:
    global gap, dirty
    if abs(gap - value) > 0.001:
        gap = value
        dirty = True


def pythagoras_vertices() -> list[tuple[float, float]]:
    vertices = [from_angle(2 * pi * (i + 0.5) / 4, scalar / sqrt(2)) for i in range(4)]
    theta = atan(gap)
    slope = rotate(sub(vertices[1], vertices[0]), theta)
    vertices.append(add(vertices[0], (slope[0] * sin(theta), slope[1] * sin(theta))))
    vertices.append(add(vertices[0], (slope[0] * cos(theta), slope[1] * cos(theta))))
    vertices.append(add(vertices[0], (slope[0] / cos(theta), slope[1] / cos(theta))))
    vertices.append(add(sub(vertices[5], vertices[1]), vertices[4]))
    vertices.append(add(sub(vertices[6], vertices[1]), vertices[0]))
    return vertices


def draw_piece(vertices: list[tuple[float, float]], indices: list[int], fill_color: int) -> None:
    py5.no_stroke()
    py5.fill(fill_color)
    py5.begin_shape()
    for index in indices:
        py5.vertex(*vertices[index])
    py5.end_shape(py5.CLOSE)


def draw_edge(vertices: list[tuple[float, float]], indices: tuple[int, int]) -> None:
    py5.stroke(0, 0, 0.1, 0.65)
    py5.stroke_weight(1)
    py5.no_fill()
    py5.begin_shape()
    for index in indices:
        py5.vertex(*vertices[index])
    py5.end_shape()


def draw_pythagoras_tile() -> None:
    vertices = pythagoras_vertices()
    domains = [
        [[0, 1, 5], [4, 6, 2, 3], [3, 7, 8]],
        [[1, 5, 6], [0, 4, 7, 8]],
    ]
    for color_index, pieces in enumerate(domains):
        for piece in pieces:
            draw_piece(vertices, piece, colors[color_index])
    for edge in ((0, 6), (1, 5), (3, 4), (7, 8)):
        draw_edge(vertices, edge)


def draw_tiling() -> None:
    py5.background(0, 0, 1)
    for row in lattice:
        for x_val, y_val in row:
            py5.push_matrix()
            py5.translate(x_val, y_val)
            draw_pythagoras_tile()
            py5.pop_matrix()
    py5.no_stroke()
    py5.fill(0, 0, 0)
    py5.text_size(14)
    py5.text(f"gap {gap:.2f}", 12, 22)


def mouse_clicked() -> None:
    set_gap(py5.constrain(py5.mouse_x / py5.width, 0, 1))


def key_pressed() -> None:
    global colors, dirty
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pythagoras_periodic_####.png"))
    elif py5.key == py5.CODED and py5.key_code == py5.LEFT:
        set_gap(max(0, gap - 0.05))
    elif py5.key == py5.CODED and py5.key_code == py5.RIGHT:
        set_gap(min(1, gap + 0.05))
    elif str(py5.key).lower() == "c":
        colors = [py5.color(py5.random(1), 0.4, 1) for _ in range(2)]
        dirty = True


py5.run_sketch()
