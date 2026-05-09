from pathlib import Path
from random import Random

import py5

from logic_lab.shared.physics2d import PolygonBody, Vec2, regular_polygon, resolve_polygon_bounds

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(21)
pieces: list[PolygonBody] = []


def reset() -> None:
    pieces.clear()
    pieces.append(
        PolygonBody(Vec2(320, 140), regular_polygon(72, 9), Vec2(0, 210), mass=12, restitution=0.5)
    )


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    reset()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def fracture(body: PolygonBody) -> list[PolygonBody]:
    result = []
    for vertex in body.local_vertices:
        tri = [Vec2(), vertex, vertex * 0.55 + Vec2.from_angle(rng.random() * py5.TWO_PI, 16)]
        result.append(
            PolygonBody(
                body.pos.copy(),
                tri,
                body.vel + vertex.normalized() * rng.uniform(80, 180),
                body.angle,
                rng.uniform(-4, 4),
                mass=1,
                restitution=0.55,
            )
        )
    return result


def draw() -> None:
    py5.background(248)
    for body in pieces[:]:
        body.step(1 / 60, Vec2(0, 360))
        event = resolve_polygon_bounds(body, py5.width, py5.height)
        if event and event.impulse > 2500 and len(pieces) < 25 and len(body.local_vertices) > 3:
            pieces.remove(body)
            pieces.extend(fracture(body))
    for body in pieces:
        py5.fill(208, 80, 70, 125)
        py5.stroke(30)
        py5.begin_shape()
        for vertex in body.vertices():
            py5.vertex(vertex.x, vertex.y)
        py5.end_shape(py5.CLOSE)


def mouse_pressed() -> None:
    reset()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fracture_dynamics_####.png"))


py5.run_sketch()
