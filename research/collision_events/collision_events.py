from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PARTICLE_COLLISION_TYPE = 1
BOUNDARY_COLLISION_TYPE = 2

space: pymunk.Space
particles: list["Particle"] = []
wall: "Boundary"


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.radius = py5.random(4, 8)
        self.col = py5.color(127)

        mass = 1.0
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, py5.height - y)

        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.0
        self.shape.collision_type = PARTICLE_COLLISION_TYPE
        self.shape.user_data = self

        space.add(self.body, self.shape)

    def change(self) -> None:
        self.col = py5.color(py5.random(100, 255), 0, py5.random(100, 255))

    def check_edge(self) -> bool:
        return to_screen_y(float(self.body.position.y)) > py5.height + self.radius

    def remove_body(self) -> None:
        space.remove(self.shape, self.body)

    def show(self) -> None:
        px = float(self.body.position.x)
        py_ = to_screen_y(float(self.body.position.y))
        py5.fill(self.col)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(px, py_)
            py5.rotate(-self.body.angle)
            py5.circle(0, 0, self.radius * 2)
            py5.line(0, 0, self.radius, 0)


class Boundary:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.collision_type = BOUNDARY_COLLISION_TYPE
        space.add(self.body, self.shape)

    def show(self) -> None:
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.no_stroke()
        py5.rect(self.x, self.y, self.w, self.h)


def handle_particle_collision(arbiter: pymunk.Arbiter, _space: pymunk.Space, _data: object) -> None:
    shape_a, shape_b = arbiter.shapes
    particle_a = shape_a.user_data
    particle_b = shape_b.user_data
    if isinstance(particle_a, Particle) and isinstance(particle_b, Particle):
        particle_a.change()
        particle_b.change()


def setup() -> None:
    global space, wall
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -100)

    wall = Boundary(py5.width / 2, py5.height - 5, py5.width, 10)

    space.on_collision(
        PARTICLE_COLLISION_TYPE,
        PARTICLE_COLLISION_TYPE,
        begin=handle_particle_collision,
    )

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    if py5.random(1) < 0.05:
        particles.append(Particle(py5.random(py5.width), 0))

    space.step(1 / 60)

    for i in range(len(particles) - 1, -1, -1):
        particle = particles[i]
        particle.show()
        if particle.check_edge():
            particle.remove_body()
            particles.pop(i)

    wall.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "collision_events_####.png"))


py5.run_sketch()
