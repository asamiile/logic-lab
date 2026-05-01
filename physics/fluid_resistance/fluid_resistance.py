from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self, x: float, y: float, mass: float) -> None:
        self.mass = mass
        self.radius = mass * 8
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

    def check_edges(self) -> None:
        if self.position.y > py5.height - self.radius:
            self.velocity.y *= -0.9
            self.position.y = py5.height - self.radius


class Liquid:
    def __init__(self, x: float, y: float, w: float, h: float, c: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

    def contains(self, mover: Mover) -> bool:
        pos = mover.position
        return self.x < pos.x < self.x + self.w and self.y < pos.y < self.y + self.h

    def calculate_drag(self, mover: Mover) -> py5.Py5Vector:
        speed = mover.velocity.mag
        drag_magnitude = self.c * speed * speed
        return mover.velocity.norm * -drag_magnitude

    def show(self) -> None:
        py5.no_stroke()
        py5.fill(220)
        py5.rect(self.x, self.y, self.w, self.h)


movers: list[Mover] = []
liquid: Liquid


def reset() -> None:
    global movers
    movers = [Mover(40 + i * 70, 0, py5.random(0.5, 3)) for i in range(9)]


def setup() -> None:
    global liquid
    py5.size(640, 240)
    reset()
    liquid = Liquid(0, py5.height / 2, py5.width, py5.height / 2, 0.1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    liquid.show()

    for mover in movers:
        if liquid.contains(mover):
            drag = liquid.calculate_drag(mover)
            mover.apply_force(drag)

        gravity = py5.Py5Vector(0, 0.1 * mover.mass)
        mover.apply_force(gravity)

        mover.update()
        mover.show()
        mover.check_edges()


def mouse_pressed() -> None:
    reset()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fluid_resistance_####.png"))


py5.run_sketch()
