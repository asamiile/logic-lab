from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

vehicles: list["Vehicle"] = []


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


class Vehicle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.r = 12
        self.max_speed = 3
        self.max_force = 0.2
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(0, 0)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def separate(self, others: list["Vehicle"]) -> None:
        desired_separation = self.r * 2
        total = py5.Py5Vector(0, 0)
        count = 0

        for other in others:
            distance = (self.position - other.position).mag
            if other is not self and 0 < distance < desired_separation:
                diff = self.position - other.position
                diff = diff.norm / distance
                total += diff
                count += 1

        if count > 0:
            total = total.norm * self.max_speed
            steer = total - self.velocity
            steer = limit_vector(steer, self.max_force)
            self.apply_force(steer)

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def show(self) -> None:
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.circle(0, 0, self.r)

    def borders(self) -> None:
        if self.position.x < -self.r:
            self.position.x = py5.width + self.r
        if self.position.y < -self.r:
            self.position.y = py5.height + self.r
        if self.position.x > py5.width + self.r:
            self.position.x = -self.r
        if self.position.y > py5.height + self.r:
            self.position.y = -self.r


def setup() -> None:
    global vehicles
    py5.size(640, 240)
    vehicles = [Vehicle(py5.random(py5.width), py5.random(py5.height)) for _ in range(25)]
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    for vehicle in vehicles:
        vehicle.separate(vehicles)
        vehicle.update()
        vehicle.borders()
        vehicle.show()


def mouse_dragged() -> None:
    vehicles.append(Vehicle(py5.mouse_x, py5.mouse_y))


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "separation_####.png"))


py5.run_sketch()
