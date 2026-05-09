from pathlib import Path
from random import Random

import py5

from logic_lab.shared.physics2d import CircleBody, Vec2, resolve_bounds, resolve_circle_collision

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(12)
bodies: list[CircleBody] = []


def make_body() -> CircleBody:
    radius = rng.uniform(12, 26)
    return CircleBody(
        pos=Vec2(rng.uniform(radius, 640 - radius), rng.uniform(radius, 260 - radius)),
        vel=Vec2(rng.uniform(-130, 130), rng.uniform(-80, 80)),
        radius=radius,
        mass=radius * radius,
        restitution=0.92,
        friction=0.015,
        spin=rng.uniform(-2.2, 2.2),
    )


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    bodies.extend(make_body() for _ in range(24))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_body(body: CircleBody) -> None:
    py5.stroke(25)
    py5.stroke_weight(1.5)
    py5.fill(80, 145, 220, 190)
    py5.circle(body.pos.x, body.pos.y, body.radius * 2)
    direction = Vec2.from_angle(body.angle, body.radius)
    py5.line(body.pos.x, body.pos.y, body.pos.x + direction.x, body.pos.y + direction.y)


def draw() -> None:
    py5.background(248)
    dt = 1 / 60
    gravity = Vec2(0, 140)

    for body in bodies:
        body.step(dt, gravity)
        resolve_bounds(body, py5.width, py5.height)

    for i, a in enumerate(bodies):
        for b in bodies[i + 1 :]:
            resolve_circle_collision(a, b)

    for body in bodies:
        draw_body(body)


def mouse_pressed() -> None:
    bodies.append(
        CircleBody(
            pos=Vec2(py5.mouse_x, py5.mouse_y),
            vel=Vec2(rng.uniform(-120, 120), rng.uniform(-180, -40)),
            radius=rng.uniform(10, 22),
            mass=400,
            restitution=0.94,
            friction=0.01,
            spin=rng.uniform(-3, 3),
        )
    )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "rigid_body_collision_####.png"))


py5.run_sketch()
