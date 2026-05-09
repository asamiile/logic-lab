from pathlib import Path

import py5
from logic_lab.shared.physics2d import PolygonBody, Vec2, regular_polygon, sat_collision

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

fixed = PolygonBody(Vec2(300, 185), regular_polygon(82, 6), angle=0.2)
moving = PolygonBody(Vec2(420, 185), regular_polygon(62, 5), angle=0.0)


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_poly(vertices: list[Vec2], color: tuple[int, int, int], alpha: int) -> None:
    py5.fill(*color, alpha)
    py5.stroke(20)
    py5.begin_shape()
    for v in vertices:
        py5.vertex(v.x, v.y)
    py5.end_shape(py5.CLOSE)


def draw() -> None:
    py5.background(250)
    fixed.angle += 0.006
    moving.pos = Vec2(py5.mouse_x, py5.mouse_y)
    moving.angle -= 0.018
    a_vertices = fixed.vertices()
    b_vertices = moving.vertices()
    result = sat_collision(a_vertices, b_vertices)
    draw_poly(a_vertices, (52, 132, 200), 130)
    draw_poly(b_vertices, (230, 86, 64), 145 if result.overlaps else 95)
    if result.overlaps:
        center = (fixed.pos + moving.pos) * 0.5
        py5.stroke(210, 40, 40)
        py5.stroke_weight(3)
        py5.line(
            center.x,
            center.y,
            center.x + result.normal.x * result.depth * 6,
            center.y + result.normal.y * result.depth * 6,
        )
    py5.no_stroke()
    py5.fill(30)
    py5.text(f"SAT overlap: {result.overlaps}  depth: {result.depth:.2f}", 18, 28)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "sat_polygon_collision_####.png"))


py5.run_sketch()
