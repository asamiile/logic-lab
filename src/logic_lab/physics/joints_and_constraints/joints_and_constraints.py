from pathlib import Path

import py5
from logic_lab.shared.physics2d import DistanceConstraint, Vec2, VerletPoint, enforce_verlet_bounds

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

points: list[VerletPoint] = []
constraints: list[DistanceConstraint] = []


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    for x in range(8):
        fixed = x in (0, 7)
        points.append(VerletPoint.at(145 + x * 50, 110 + (x % 2) * 18, fixed=fixed, radius=6))
    for i in range(len(points) - 1):
        constraints.append(DistanceConstraint(points[i], points[i + 1], 50, 0.9))
    for i in range(len(points) - 2):
        constraints.append(DistanceConstraint(points[i], points[i + 2], 92, 0.35))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(248)
    for p in points:
        p.apply_force(Vec2(0, 680))
        p.step(1 / 60, damping=0.996)
    if py5.is_mouse_pressed:
        points[len(points) // 2].pos = Vec2(py5.mouse_x, py5.mouse_y)
    for _ in range(12):
        for c in constraints:
            c.solve()
        enforce_verlet_bounds(points, py5.width, py5.height)
    py5.stroke(26)
    py5.stroke_weight(3)
    for c in constraints:
        py5.line(c.a.pos.x, c.a.pos.y, c.b.pos.x, c.b.pos.y)
    py5.no_stroke()
    for p in points:
        py5.fill(25 if p.fixed else 232, 104, 82)
        py5.circle(p.pos.x, p.pos.y, p.radius * 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "joints_and_constraints_####.png"))


py5.run_sketch()
