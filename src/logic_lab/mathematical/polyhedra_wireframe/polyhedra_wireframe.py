from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
current_polyhedron = 0

TETRAHEDRON_VERTS = [
    (1, 1, 1),
    (1, -1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
]
TETRAHEDRON_EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

CUBE_VERTS = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
]
CUBE_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]

OCTAHEDRON_VERTS = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
]
OCTAHEDRON_EDGES = [
    (0, 2),
    (0, 3),
    (0, 4),
    (0, 5),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (2, 4),
    (2, 5),
    (3, 4),
    (3, 5),
]


def rotate_x(
    vertices: list[tuple[float, float, float]], angle: float
) -> list[tuple[float, float, float]]:
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [(x, y * cos_a - z * sin_a, y * sin_a + z * cos_a) for x, y, z in vertices]


def rotate_y(
    vertices: list[tuple[float, float, float]], angle: float
) -> list[tuple[float, float, float]]:
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [(x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a) for x, y, z in vertices]


def project_to_2d(vertices: list[tuple[float, float, float]]) -> list[tuple[float, float]]:
    projected = []
    for x, y, z in vertices:
        scale = 200 / (4 + z)
        projected.append((x * scale, y * scale))
    return projected


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    polyhedra = [
        (TETRAHEDRON_VERTS, TETRAHEDRON_EDGES, "Tetrahedron"),
        (CUBE_VERTS, CUBE_EDGES, "Cube"),
        (OCTAHEDRON_VERTS, OCTAHEDRON_EDGES, "Octahedron"),
    ]

    verts, edges, name = polyhedra[current_polyhedron % 3]

    verts_rotated = rotate_x(verts, time_value * 0.5)
    verts_rotated = rotate_y(verts_rotated, time_value * 0.7)

    verts_2d = project_to_2d(verts_rotated)

    py5.no_fill()
    py5.stroke_weight(2)
    py5.stroke(120 + time_value * 50 % 360, 70, 100)

    for v1_idx, v2_idx in edges:
        x1, y1 = verts_2d[v1_idx]
        x2, y2 = verts_2d[v2_idx]
        py5.line(x1, y1, x2, y2)

    py5.fill(200, 50, 80)
    py5.no_stroke()
    for x, y in verts_2d:
        py5.circle(x, y, 5)

    py5.fill(0, 0, 100)
    py5.text_size(14)
    py5.text(f"{name}", -50, -py5.height / 2 + 30)


def key_pressed() -> None:
    global current_polyhedron
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "polyhedra_wireframe_####.png"))
    elif py5.key == "n":
        current_polyhedron += 1


py5.run_sketch()
