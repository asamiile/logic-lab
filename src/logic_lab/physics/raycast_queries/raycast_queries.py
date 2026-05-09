from pathlib import Path

import py5
from logic_lab.shared.physics2d import (
    PolygonBody,
    Vec2,
    raycast_polygon,
    rectangle_vertices,
    regular_polygon,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

obstacles = [
    PolygonBody(Vec2(190, 150), rectangle_vertices(120, 48), angle=0.4),
    PolygonBody(Vec2(410, 210), regular_polygon(68, 5), angle=0.2),
    PolygonBody(Vec2(500, 95), rectangle_vertices(80, 70), angle=-0.25),
]


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(246)
    origin = Vec2(80, py5.height * 0.5)
    mouse = Vec2(py5.mouse_x, py5.mouse_y)
    for obstacle in obstacles:
        obstacle.angle += 0.002
        py5.fill(42, 90, 120, 80)
        py5.stroke(25)
        py5.begin_shape()
        for vertex in obstacle.vertices():
            py5.vertex(vertex.x, vertex.y)
        py5.end_shape(py5.CLOSE)
    closest = None
    direction = mouse - origin
    for obstacle in obstacles:
        hit = raycast_polygon(origin, direction, obstacle.vertices())
        if hit and (closest is None or hit.distance < closest.distance):
            closest = hit
    py5.stroke(230, 70, 60)
    py5.stroke_weight(2)
    end = closest.point if closest else mouse
    py5.line(origin.x, origin.y, end.x, end.y)
    py5.no_stroke()
    py5.fill(30)
    py5.circle(origin.x, origin.y, 10)
    if closest:
        py5.fill(230, 70, 60)
        py5.circle(closest.point.x, closest.point.y, 12)
        py5.stroke(230, 70, 60)
        py5.line(
            closest.point.x,
            closest.point.y,
            closest.point.x + closest.normal.x * 35,
            closest.point.y + closest.normal.y * 35,
        )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "raycast_queries_####.png"))


py5.run_sketch()
