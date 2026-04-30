from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
OFFSET = 25

debug = True
vehicle: "Vehicle"


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


class Vehicle:
    def __init__(self, x: float, y: float) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(3, 4)
        self.position = py5.Py5Vector(x, y)
        self.r = 6
        self.max_speed = 3
        self.max_force = 0.15

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def boundaries(self, offset: float) -> None:
        desired = None

        if self.position.x < offset:
            desired = py5.Py5Vector(self.max_speed, self.velocity.y)
        elif self.position.x > py5.width - offset:
            desired = py5.Py5Vector(-self.max_speed, self.velocity.y)

        if self.position.y < offset:
            desired = py5.Py5Vector(self.velocity.x, self.max_speed)
        elif self.position.y > py5.height - offset:
            desired = py5.Py5Vector(self.velocity.x, -self.max_speed)

        if desired is not None and desired.mag > 0:
            desired = desired.norm * self.max_speed
            steer = desired - self.velocity
            steer = limit_vector(steer, self.max_force)
            self.apply_force(steer)

    def show(self) -> None:
        angle = self.velocity.heading

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(angle)
            py5.begin_shape()
            py5.vertex(self.r * 2, 0)
            py5.vertex(-self.r * 2, -self.r)
            py5.vertex(-self.r * 2, self.r)
            py5.end_shape(py5.CLOSE)


def setup() -> None:
    global vehicle
    py5.size(640, 240)
    vehicle = Vehicle(py5.width / 2, py5.height / 2)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    if debug:
        py5.stroke(0)
        py5.no_fill()
        py5.rect_mode(py5.CENTER)
        py5.rect(py5.width / 2, py5.height / 2, py5.width - OFFSET * 2, py5.height - OFFSET * 2)

    vehicle.boundaries(OFFSET)
    vehicle.update()
    vehicle.show()


def mouse_pressed() -> None:
    global debug
    debug = not debug


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "stay_within_walls_####.png"))


py5.run_sketch()
