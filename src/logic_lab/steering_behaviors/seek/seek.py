from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


class Vehicle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = 6
        self.max_speed = 8
        self.max_force = 0.2

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def seek(self, target: py5.Py5Vector) -> None:
        desired = target - self.position
        if desired.mag > 0:
            desired = desired.norm * self.max_speed

        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force)
        self.apply_force(steer)

    def show(self) -> None:
        angle = self.velocity.heading

        py5.fill(127)
        py5.stroke(0)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(angle)
            py5.begin_shape()
            py5.vertex(self.r * 2, 0)
            py5.vertex(-self.r * 2, -self.r)
            py5.vertex(-self.r * 2, self.r)
            py5.end_shape(py5.CLOSE)


vehicle: Vehicle


def setup() -> None:
    global vehicle
    py5.size(640, 240)
    vehicle = Vehicle(py5.width / 2, py5.height / 2)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)

    py5.fill(127)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.circle(mouse.x, mouse.y, 48)

    vehicle.seek(mouse)
    vehicle.update()
    vehicle.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "seek_####.png"))


py5.run_sketch()
