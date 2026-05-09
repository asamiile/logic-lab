from pathlib import Path

import py5

from logic_lab.shared.physics2d import Vec2, build_cloth, enforce_verlet_bounds

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

points, constraints = build_cloth(24, 13, 18, Vec2(112, 52), fixed_top=True)


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(246)
    wind = Vec2(py5.sin(py5.frame_count * 0.025) * 70, 0)
    gravity = Vec2(0, 540)
    dt = 1 / 60

    for point in points:
        point.apply_force(gravity + wind)
        point.step(dt, damping=0.992)

    if py5.is_mouse_pressed:
        for point in points:
            delta = point.pos - Vec2(py5.mouse_x, py5.mouse_y)
            if delta.mag() < 42 and not point.fixed:
                point.pos = point.pos + delta.normalized() * 8

    for _ in range(7):
        for constraint in constraints:
            constraint.solve()
        enforce_verlet_bounds(points, py5.width, py5.height)

    py5.stroke(38, 62, 76, 165)
    py5.stroke_weight(1.3)
    for constraint in constraints:
        py5.line(constraint.a.pos.x, constraint.a.pos.y, constraint.b.pos.x, constraint.b.pos.y)

    py5.no_stroke()
    for point in points:
        py5.fill(30 if point.fixed else 58, 139, 138)
        py5.circle(point.pos.x, point.pos.y, point.radius * 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mass_spring_cloth_####.png"))


py5.run_sketch()
