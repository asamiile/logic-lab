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
        py5.ellipse(self.position.x, self.position.y, self.radius * 2, self.radius * 2)

    def check_edges(self) -> None:
        if self.position.x > py5.width - self.radius:
            self.position.x = py5.width - self.radius
            self.velocity.x *= -1
        elif self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= -1
        if self.position.y > py5.height - self.radius:
            self.position.y = py5.height - self.radius
            self.velocity.y *= -1


mover_a: Mover
mover_b: Mover


def setup() -> None:
    global mover_a, mover_b
    py5.size(640, 240)
    mover_a = Mover(200, 30, 10)
    mover_b = Mover(440, 30, 2)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    gravity = py5.Py5Vector(0, 0.1)

    gravity_a = gravity * mover_a.mass
    mover_a.apply_force(gravity_a)

    gravity_b = gravity * mover_b.mass
    mover_b.apply_force(gravity_b)

    if py5.is_mouse_pressed:
        wind = py5.Py5Vector(0.1, 0)
        mover_a.apply_force(wind)
        mover_b.apply_force(wind)

    mover_a.update()
    mover_a.show()
    mover_a.check_edges()

    mover_b.update()
    mover_b.show()
    mover_b.check_edges()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "gravity_scaled_by_mass_####.png"))


py5.run_sketch()
