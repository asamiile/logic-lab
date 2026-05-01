from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

debug = True
path: "Path"
vehicle1: "Vehicle"
vehicle2: "Vehicle"


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


def get_normal_point(position: py5.Py5Vector, a: py5.Py5Vector, b: py5.Py5Vector) -> py5.Py5Vector:
    vector_a = position - a
    vector_b = b - a
    if vector_b.mag == 0:
        return a.copy

    vector_b = vector_b.norm
    projection = vector_a.x * vector_b.x + vector_a.y * vector_b.y
    vector_b *= projection
    return a + vector_b


class Path:
    def __init__(self) -> None:
        self.radius = 20
        self.start = py5.Py5Vector(0, py5.height / 3)
        self.end = py5.Py5Vector(py5.width, 2 * py5.height / 3)

    def show(self) -> None:
        py5.stroke_weight(self.radius * 2)
        py5.stroke(0, 50)
        py5.line(self.start.x, self.start.y, self.end.x, self.end.y)

        py5.stroke_weight(1)
        py5.stroke(0)
        py5.line(self.start.x, self.start.y, self.end.x, self.end.y)


class Vehicle:
    def __init__(self, x: float, y: float, max_speed: float, max_force: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(2, 0)
        self.r = 4
        self.max_speed = max_speed
        self.max_force = max_force

    def run(self) -> None:
        self.update()
        self.show()

    def follow(self, p: Path) -> None:
        future = self.velocity.copy
        if future.mag > 0:
            future = future.norm * 25
        future += self.position

        normal_point = get_normal_point(future, p.start, p.end)

        path_direction = p.end - p.start
        if path_direction.mag > 0:
            path_direction = path_direction.norm * 25
        target = normal_point + path_direction

        distance = (normal_point - future).mag
        if distance > p.radius:
            self.seek(target)

        if debug:
            py5.fill(127)
            py5.stroke(0)
            py5.stroke_weight(1)
            py5.line(self.position.x, self.position.y, future.x, future.y)
            py5.circle(future.x, future.y, 4)

            py5.line(future.x, future.y, normal_point.x, normal_point.y)
            py5.circle(normal_point.x, normal_point.y, 4)

            if distance > p.radius:
                py5.fill(255, 0, 0)
            else:
                py5.fill(127)
            py5.no_stroke()
            py5.circle(target.x + path_direction.x, target.y + path_direction.y, 8)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def seek(self, target: py5.Py5Vector) -> None:
        desired = target - self.position
        if desired.mag == 0:
            return

        desired = desired.norm * self.max_speed
        steer = desired - self.velocity
        steer = limit_vector(steer, self.max_force)
        self.apply_force(steer)

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def borders(self, p: Path) -> None:
        if self.position.x > p.end.x + self.r:
            self.position.x = p.start.x - self.r
            self.position.y = p.start.y + (self.position.y - p.end.y)

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
    global path, vehicle1, vehicle2
    py5.size(640, 240)
    path = Path()
    vehicle1 = Vehicle(0, py5.height / 2, 2, 0.02)
    vehicle2 = Vehicle(0, py5.height / 2, 3, 0.05)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    path.show()

    vehicle1.follow(path)
    vehicle2.follow(path)

    vehicle1.run()
    vehicle2.run()

    vehicle1.borders(path)
    vehicle2.borders(path)


def key_pressed() -> None:
    global debug
    if py5.key == " ":
        debug = not debug
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "path_following_simple_####.png"))


py5.run_sketch()
