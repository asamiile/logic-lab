from math import floor
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

debug = True
flow_field: "FlowField"
vehicles: list["Vehicle"] = []


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


def constrain(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


class FlowField:
    def __init__(self, resolution: int) -> None:
        self.resolution = resolution
        self.cols = py5.width // self.resolution
        self.rows = py5.height // self.resolution
        self.field: list[list[py5.Py5Vector]] = [
            [py5.Py5Vector(0, 0) for _ in range(self.rows)] for _ in range(self.cols)
        ]
        self.init()

    def init(self) -> None:
        py5.noise_seed(int(py5.random(10000)))
        xoff = 0.0
        for i in range(self.cols):
            yoff = 0.0
            for j in range(self.rows):
                angle = py5.remap(py5.noise(xoff, yoff), 0, 1, 0, py5.TWO_PI)
                self.field[i][j] = py5.Py5Vector(py5.cos(angle), py5.sin(angle))
                yoff += 0.1
            xoff += 0.1

    def show(self) -> None:
        for i in range(self.cols):
            for j in range(self.rows):
                w = py5.width / self.cols
                h = py5.height / self.rows
                v = self.field[i][j].copy
                v = v.norm * (w * 0.5)
                x = i * w + w / 2
                y = j * h + h / 2
                py5.stroke(0)
                py5.stroke_weight(1)
                py5.line(x, y, x + v.x, y + v.y)

    def lookup(self, position: py5.Py5Vector) -> py5.Py5Vector:
        column = constrain(floor(position.x / self.resolution), 0, self.cols - 1)
        row = constrain(floor(position.y / self.resolution), 0, self.rows - 1)
        return self.field[column][row].copy


class Vehicle:
    def __init__(self, x: float, y: float, max_speed: float, max_force: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(0, 0)
        self.r = 4
        self.max_speed = max_speed
        self.max_force = max_force

    def run(self) -> None:
        self.update()
        self.borders()
        self.show()

    def follow(self, flow: FlowField) -> None:
        desired = flow.lookup(self.position)
        desired *= self.max_speed
        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force)
        self.apply_force(steer)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def borders(self) -> None:
        if self.position.x < -self.r:
            self.position.x = py5.width + self.r
        if self.position.y < -self.r:
            self.position.y = py5.height + self.r
        if self.position.x > py5.width + self.r:
            self.position.x = -self.r
        if self.position.y > py5.height + self.r:
            self.position.y = -self.r

    def show(self) -> None:
        theta = self.velocity.heading
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(theta)
            py5.begin_shape()
            py5.vertex(self.r * 2, 0)
            py5.vertex(-self.r * 2, -self.r)
            py5.vertex(-self.r * 2, self.r)
            py5.end_shape(py5.CLOSE)


def setup() -> None:
    global flow_field, vehicles
    py5.size(640, 240)
    flow_field = FlowField(20)
    vehicles = [
        Vehicle(py5.random(py5.width), py5.random(py5.height), py5.random(2, 5), py5.random(0.1, 0.5))
        for _ in range(120)
    ]
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    if debug:
        flow_field.show()

    for vehicle in vehicles:
        vehicle.follow(flow_field)
        vehicle.run()


def key_pressed() -> None:
    global debug
    if py5.key == " ":
        debug = not debug
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flow_field_####.png"))


def mouse_pressed() -> None:
    flow_field.init()


py5.run_sketch()
