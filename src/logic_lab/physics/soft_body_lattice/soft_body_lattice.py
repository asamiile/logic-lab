from pathlib import Path

import py5
from logic_lab.shared.physics2d import DistanceConstraint, Vec2, VerletPoint, enforce_verlet_bounds

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

points: list[VerletPoint] = []
constraints: list[DistanceConstraint] = []
cols = 7
rows = 6


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    for y in range(rows):
        for x in range(cols):
            points.append(VerletPoint.at(260 + x * 24, 115 + y * 24, radius=4))
    for y in range(rows):
        for x in range(cols):
            idx = y * cols + x
            if x < cols - 1:
                constraints.append(DistanceConstraint(points[idx], points[idx + 1], 24, 0.75))
            if y < rows - 1:
                constraints.append(DistanceConstraint(points[idx], points[idx + cols], 24, 0.75))
            if x < cols - 1 and y < rows - 1:
                constraints.append(
                    DistanceConstraint(points[idx], points[idx + cols + 1], 34, 0.35)
                )
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(249)
    center = Vec2(py5.mouse_x, py5.mouse_y)
    for p in points:
        p.apply_force(Vec2(0, 380))
        if py5.is_mouse_pressed:
            delta = p.pos - center
            if 0 < delta.mag() < 90:
                p.apply_force(delta.normalized() * 2600)
        p.step(1 / 60, 0.99)
    for _ in range(10):
        for c in constraints:
            c.solve()
        enforce_verlet_bounds(points, py5.width, py5.height)
    py5.no_stroke()
    py5.fill(55, 155, 132, 130)
    for y in range(rows - 1):
        py5.begin_shape(py5.QUADS)
        for x in range(cols - 1):
            for idx in (y * cols + x, y * cols + x + 1, (y + 1) * cols + x + 1, (y + 1) * cols + x):
                py5.vertex(points[idx].pos.x, points[idx].pos.y)
        py5.end_shape()
    py5.stroke(25, 120)
    for c in constraints:
        py5.line(c.a.pos.x, c.a.pos.y, c.b.pos.x, c.b.pos.y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "soft_body_lattice_####.png"))


py5.run_sketch()
