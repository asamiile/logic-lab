from pathlib import Path
from random import Random

import py5

from logic_lab.shared.physics2d import (
    PolygonBody,
    Vec2,
    rectangle_vertices,
    regular_polygon,
    resolve_polygon_bounds,
    resolve_polygon_collision,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(18)
bodies: list[PolygonBody] = []


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    for _ in range(10):
        shape = (
            rectangle_vertices(rng.uniform(26, 52), rng.uniform(18, 42))
            if rng.random() < 0.55
            else regular_polygon(rng.uniform(18, 34), rng.randint(3, 6))
        )
        bodies.append(
            PolygonBody(
                Vec2(rng.uniform(80, 560), rng.uniform(40, 190)),
                shape,
                Vec2(rng.uniform(-55, 55), rng.uniform(-20, 20)),
                rng.random() * py5.TWO_PI,
                rng.uniform(-1.8, 1.8),
                mass=3,
                restitution=0.62,
            )
        )
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(247)
    gravity = Vec2(0, 260)
    for body in bodies:
        body.step(1 / 60, gravity)
        resolve_polygon_bounds(body, py5.width, py5.height)
    for i, a in enumerate(bodies):
        for b in bodies[i + 1 :]:
            resolve_polygon_collision(a, b)
    for body in bodies:
        py5.fill(92, 142, 202, 145)
        py5.stroke(22)
        py5.begin_shape()
        for vertex in body.vertices():
            py5.vertex(vertex.x, vertex.y)
        py5.end_shape(py5.CLOSE)


def mouse_pressed() -> None:
    bodies.append(
        PolygonBody(
            Vec2(py5.mouse_x, py5.mouse_y),
            rectangle_vertices(42, 28),
            Vec2(rng.uniform(-40, 40), -90),
            rng.random(),
            rng.uniform(-3, 3),
            mass=3,
            restitution=0.65,
        )
    )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "rotating_rigid_bodies_####.png"))


py5.run_sketch()
