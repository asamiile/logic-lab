from pathlib import Path

import py5
from logic_lab.shared.physics2d import DistanceConstraint, Vec2, VerletPoint, enforce_verlet_bounds

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

points: list[VerletPoint] = []
constraints: list[DistanceConstraint] = []


def setup() -> None:
    py5.size(640, 360)
    anchor = VerletPoint.at(320, 70, fixed=True, radius=7)
    points.append(anchor)
    previous = anchor
    for i in range(1, 18):
        point = VerletPoint.at(320 + py5.sin(i * 0.6) * 18, 70 + i * 14, radius=5)
        points.append(point)
        constraints.append(DistanceConstraint(previous, point, 16, stiffness=0.95))
        previous = point
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(250)
    gravity = Vec2(0, 850)
    dt = 1 / 60

    if py5.is_mouse_pressed:
        points[-1].pos = Vec2(py5.mouse_x, py5.mouse_y)

    for point in points:
        point.apply_force(gravity)
        point.step(dt)

    for _ in range(8):
        for constraint in constraints:
            constraint.solve()
        enforce_verlet_bounds(points, py5.width, py5.height)

    py5.stroke(30)
    py5.stroke_weight(3)
    for constraint in constraints:
        py5.line(constraint.a.pos.x, constraint.a.pos.y, constraint.b.pos.x, constraint.b.pos.y)

    py5.no_stroke()
    for point in points:
        py5.fill(20 if point.fixed else 225, 80, 90)
        py5.circle(point.pos.x, point.pos.y, point.radius * 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "verlet_constraints_####.png"))


py5.run_sketch()
