from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self, x: float, y: float, m: float) -> None:
        self.mass = m
        self.radius = m * 8
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
        py5.circle(self.position.x, self.position.y, self.radius * 2)

    def contact_edge(self) -> bool:
        return self.position.y > py5.height - self.radius - 1

    def bounce_edges(self) -> None:
        bounce = -0.9
        if self.position.x > py5.width - self.radius:
            self.position.x = py5.width - self.radius
            self.velocity.x *= bounce
        elif self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= bounce
        if self.position.y > py5.height - self.radius:
            self.position.y = py5.height - self.radius
            self.velocity.y *= bounce


mover: Mover


def setup() -> None:
    global mover
    py5.size(640, 240)
    mover = Mover(py5.width / 2, 30, 5)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    gravity = py5.Py5Vector(0, 1)
    mover.apply_force(gravity)

    if py5.is_mouse_pressed:
        wind = py5.Py5Vector(0.5, 0)
        mover.apply_force(wind)

    if mover.contact_edge():
        c = 0.1
        friction = mover.velocity.norm * -c
        mover.apply_force(friction)

    mover.bounce_edges()
    mover.update()
    mover.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "including_friction_####.png"))


py5.run_sketch()
