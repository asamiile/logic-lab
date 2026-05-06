import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

G = 1.0


class Body:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.mass = 8.0
        self.r = math.sqrt(self.mass) * 2

    def attract(self, other: "Body") -> None:
        force = self.position - other.position
        d = py5.constrain(force.mag, 5, 25)
        strength = (G * self.mass * other.mass) / (d * d)
        other.apply_force(force.norm * strength)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force / self.mass

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127, 100)
        py5.circle(self.position.x, self.position.y, self.r * 4)


body_a: Body
body_b: Body


def setup() -> None:
    global body_a, body_b
    py5.size(640, 240)
    body_a = Body(320, 40)
    body_a.velocity = py5.Py5Vector(1, 0)
    body_b = Body(320, 200)
    body_b.velocity = py5.Py5Vector(-1, 0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    body_a.attract(body_b)
    body_b.attract(body_a)

    body_a.update()
    body_a.show()
    body_b.update()
    body_b.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "two_body_attraction_####.png"))


py5.run_sketch()
