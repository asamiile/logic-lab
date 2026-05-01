from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self, x: float, y: float, mass: float) -> None:
        self.mass = mass
        self.radius = self.mass * 8
        self.position = py5.Py5Vector(x, y)
        self.angle = 0.0
        self.angle_velocity = 0.0
        self.angle_acceleration = 0.0
        self.velocity = py5.Py5Vector(py5.random(-1, 1), py5.random(-1, 1))
        self.acceleration = py5.Py5Vector(0, 0)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force / self.mass

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.angle_acceleration = self.acceleration.x / 10.0
        self.angle_velocity += self.angle_acceleration
        self.angle_velocity = py5.constrain(self.angle_velocity, -0.1, 0.1)
        self.angle += self.angle_velocity
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke_weight(2)
        py5.stroke(0)
        py5.fill(127, 127)
        py5.rect_mode(py5.CENTER)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(self.angle)
            py5.circle(0, 0, self.radius * 2)
            py5.line(0, 0, self.radius, 0)


class Attractor:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.mass = 20
        self.g = 1

    def attract(self, mover: Mover) -> py5.Py5Vector:
        force = self.position - mover.position
        distance = py5.constrain(force.mag, 5, 25)
        strength = (self.g * self.mass * mover.mass) / (distance * distance)
        return force.norm * strength

    def display(self) -> None:
        py5.ellipse_mode(py5.CENTER)
        py5.stroke(0)
        py5.fill(175, 200)
        py5.ellipse(self.position.x, self.position.y, self.mass * 2, self.mass * 2)


movers: list[Mover]
attractor: Attractor


def setup() -> None:
    global movers, attractor
    py5.size(640, 240)
    movers = [
        Mover(py5.random(py5.width), py5.random(py5.height), py5.random(0.1, 2))
        for _ in range(20)
    ]
    attractor = Attractor()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    attractor.display()

    for mover in movers:
        force = attractor.attract(mover)
        mover.apply_force(force)
        mover.update()
        mover.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "forces_with_arbitrary_angular_motion_####.png"))


py5.run_sketch()
