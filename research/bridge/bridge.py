from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
bridge: "Bridge"
boxes: list["Box"] = []


def to_physics_y(screen_y: float) -> float:
    return py5.height - screen_y


def to_screen_y(physics_y: float) -> float:
    return py5.height - physics_y


class Box:
    def __init__(self, x: float, y: float) -> None:
        self.w = py5.random(8, 16)
        self.h = py5.random(8, 16)

        mass = 1.0
        moment = pymunk.moment_for_box(mass, (self.w, self.h))
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, to_physics_y(y))
        self.body.velocity = (py5.random(-5, 5), 0)
        self.body.angular_velocity = -0.1

        self.shape = pymunk.Poly.create_box(self.body, (self.w, self.h))
        self.shape.elasticity = 0.6
        self.shape.friction = 0.3
        space.add(self.body, self.shape)

    def show(self) -> None:
        pos = self.body.position
        angle = self.body.angle
        py5.rect_mode(py5.CENTER)
        py5.fill(0)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(float(pos.x), to_screen_y(float(pos.y)))
            py5.rotate(-angle)
            py5.rect(0, 0, self.w, self.h)


class Bridge:
    def __init__(self, length: float) -> None:
        self.r = length / 2
        self.length = length
        self.particles: list[pymunk.Body] = []
        self.constraints: list[pymunk.Constraint] = []
        y = 50

        for x in range(0, int(py5.width + length), int(length)):
            mass = 1.0
            moment = pymunk.moment_for_circle(mass, 0, self.r)
            body = pymunk.Body(mass, moment)
            body.position = (x, to_physics_y(y))
            shape = pymunk.Circle(body, self.r)
            shape.elasticity = 0.6
            shape.friction = 0.0
            self.particles.append(body)
            space.add(body, shape)

        self.particles[0].body_type = pymunk.Body.STATIC
        self.particles[-1].body_type = pymunk.Body.STATIC

        for i in range(len(self.particles) - 1):
            joint = pymunk.PinJoint(self.particles[i], self.particles[i + 1], (0, 0), (0, 0))
            joint.distance = length
            self.constraints.append(joint)
            space.add(joint)

    def show(self) -> None:
        py5.fill(127)
        py5.no_stroke()
        for particle in self.particles:
            with py5.push_matrix():
                py5.translate(float(particle.position.x), to_screen_y(float(particle.position.y)))
                py5.circle(0, 0, self.r * 2)


def setup() -> None:
    global space, bridge
    py5.size(640, 240)
    space = pymunk.Space()
    space.gravity = (0, -900)
    bridge = Bridge(16)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    if py5.random(1) < 0.025:
        boxes.append(Box(py5.width / 2, -50))

    bridge.show()

    for box in boxes:
        box.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "bridge_####.png"))


py5.run_sketch()
