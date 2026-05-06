from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

G = 1.0


class Body:
    def __init__(self, x: float, y: float, mass: float) -> None:
        self.mass = mass
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force / self.mass

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127, 127)
        py5.circle(self.position.x, self.position.y, self.mass * 16)

    def attract(self, other: "Body") -> py5.Py5Vector:
        force = self.position - other.position
        distance = py5.constrain(force.mag, 5, 25)
        strength = (G * self.mass * other.mass) / (distance * distance)
        return force.norm * strength


bodies: list[Body]


def setup() -> None:
    global bodies
    py5.size(640, 240)
    bodies = [
        Body(py5.random(py5.width), py5.random(py5.height), py5.random(0.1, 2)) for _ in range(10)
    ]
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    for i, body in enumerate(bodies):
        for j, other in enumerate(bodies):
            if i != j:
                force = other.attract(body)
                body.apply_force(force)

        body.update()
        body.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "n_bodies_####.png"))


py5.run_sketch()
