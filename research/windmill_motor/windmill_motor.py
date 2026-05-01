from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
windmill: "Windmill"
particles: list["Particle"] = []


def to_physics_y(screen_y: float) -> float:
    return py5.height - screen_y


def to_screen_y(physics_y: float) -> float:
    return py5.height - physics_y


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.r = 8
        mass = 1.0
        moment = pymunk.moment_for_circle(mass, 0, self.r)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, to_physics_y(y))
        self.shape = pymunk.Circle(self.body, self.r)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.3
        space.add(self.body, self.shape)

    def show(self) -> None:
        pos = self.body.position
        angle = self.body.angle
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(float(pos.x), to_screen_y(float(pos.y)))
            py5.rotate(-angle)
            py5.circle(0, 0, self.r * 2)
            py5.line(0, 0, self.r, 0)


class Windmill:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.w = w
        self.h = h

        mass = 5.0
        moment = pymunk.moment_for_box(mass, (w, h))
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, to_physics_y(y))
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.elasticity = 0.2
        self.shape.friction = 0.4
        space.add(self.body, self.shape)

        pivot = pymunk.PivotJoint(space.static_body, self.body, (x, to_physics_y(y)))
        pivot.collide_bodies = False
        space.add(pivot)

    def spin(self) -> None:
        # Match Matter.js: small force at the right tip of the bar.
        force = (0.0, 0.001 * 100000.0)
        self.body.apply_force_at_local_point(force, (self.w / 2, 0))

    def show(self) -> None:
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(float(self.body.position.x), to_screen_y(float(self.body.position.y)))
            py5.rotate(-self.body.angle)
            py5.rect(0, 0, self.w, self.h)
        py5.line(
            float(self.body.position.x),
            to_screen_y(float(self.body.position.y)),
            float(self.body.position.x),
            py5.height,
        )


def setup() -> None:
    global space, windmill
    py5.size(640, 240)
    space = pymunk.Space()
    space.gravity = (0, -900)
    windmill = Windmill(py5.width / 2, py5.height - 50, 120, 10)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    if py5.random(1) < 0.05:
        particles.append(Particle(py5.width / 2 + py5.random(-60, 60), 0))

    windmill.spin()
    space.step(1 / 60)

    windmill.show()
    for particle in particles:
        particle.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "windmill_motor_####.png"))


py5.run_sketch()
