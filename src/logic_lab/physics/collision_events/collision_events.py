from pathlib import Path
from random import Random

import py5
from logic_lab.shared.physics2d import (
    CircleBody,
    CollisionEvent,
    Vec2,
    resolve_bounds,
    resolve_circle_collision,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(31)
bodies: list[CircleBody] = []
events: list[tuple[CollisionEvent, int]] = []


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    for _ in range(14):
        radius = rng.uniform(13, 24)
        bodies.append(
            CircleBody(
                pos=Vec2(rng.uniform(radius, 640 - radius), rng.uniform(radius, 360 - radius)),
                vel=Vec2(rng.uniform(-150, 150), rng.uniform(-130, 130)),
                radius=radius,
                mass=radius,
                restitution=0.97,
                friction=0.0,
            )
        )
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(252)
    dt = 1 / 60
    events[:] = [(event, age + 1) for event, age in events if age < 35]

    for body in bodies:
        body.step(dt)
        event = resolve_bounds(body, py5.width, py5.height)
        if event:
            events.append((event, 0))

    for i, a in enumerate(bodies):
        for b in bodies[i + 1 :]:
            event = resolve_circle_collision(a, b)
            if event and event.impulse > 0:
                events.append((event, 0))

    for body in bodies:
        py5.stroke(20)
        py5.stroke_weight(1.5)
        py5.fill(235)
        py5.circle(body.pos.x, body.pos.y, body.radius * 2)
        py5.stroke(80, 120, 170, 180)
        py5.line(
            body.pos.x, body.pos.y, body.pos.x + body.vel.x * 0.12, body.pos.y + body.vel.y * 0.12
        )

    for event, age in events:
        alpha = max(0, 220 - age * 6)
        scale = 22 + age * 1.6
        py5.stroke(230, 65, 65, alpha)
        py5.stroke_weight(2)
        py5.no_fill()
        py5.circle(event.point.x, event.point.y, scale)
        py5.line(
            event.point.x,
            event.point.y,
            event.point.x + event.normal.x * scale,
            event.point.y + event.normal.y * scale,
        )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "collision_events_####.png"))


py5.run_sketch()
