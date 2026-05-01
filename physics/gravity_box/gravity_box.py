from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# pymunk uses y-up coordinates; py5 uses y-down.
# Coordinate mapping: screen_y = height - pymunk_y
# Gravity (0, -900) in pymunk y-up space = falling downward on screen.

space: pymunk.Space
box_shape: pymunk.Poly


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


def draw_poly(shape: pymunk.Poly) -> None:
    body = shape.body
    verts = [body.local_to_world(v) for v in shape.get_vertices()]
    py5.begin_shape()
    for v in verts:
        py5.vertex(float(v.x), to_screen_y(float(v.y)))
    py5.end_shape(py5.CLOSE)


def setup() -> None:
    global space, box_shape
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -1000)  # y-up: ~1000px/s² matches Matter.js default

    # Box: screen (100, 100) → pymunk (100, height-100) = (100, 140)
    mass = 1.0
    size = (50, 50)
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
    body.position = (100, py5.height - 100)
    body.velocity = (5 * 60, 0)   # Matter.js: 5 px/frame * 60 fps = 300 px/s
    body.angular_velocity = 0.1 * 60  # Matter.js: 0.1 rad/frame * 60 fps = 6 rad/s

    box_shape = pymunk.Poly.create_box(body, size)
    box_shape.friction = 0.01
    box_shape.elasticity = 0.75
    space.add(body, box_shape)

    # Ground: screen y = height-5 → pymunk y = 5; radius 5 → total 10px thick
    # elasticity=1.0 so effective = box(0.75) * ground(1.0) = 0.75, matching Matter.js max() behavior
    ground = pymunk.Segment(space.static_body, (0, 5), (py5.width, 5), 5)
    ground.friction = 0.1
    ground.elasticity = 1.0
    space.add(ground)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    # Ground
    py5.stroke(0)
    py5.stroke_weight(10)
    py5.no_fill()
    py5.line(0, to_screen_y(5), py5.width, to_screen_y(5))

    # Box
    py5.fill(200)
    py5.stroke(0)
    py5.stroke_weight(1)
    draw_poly(box_shape)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "gravity_box_####.png"))


py5.run_sketch()
