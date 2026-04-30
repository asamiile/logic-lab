from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

debug = True
path: "Path"
car1: "Vehicle"
car2: "Vehicle"


def limit_vector(vector: py5.Py5Vector, max_value: float) -> py5.Py5Vector:
    if vector.mag > max_value:
        return vector.norm * max_value
    return vector


def get_normal_point(p: py5.Py5Vector, a: py5.Py5Vector, b: py5.Py5Vector) -> py5.Py5Vector:
    ap = p - a
    ab = b - a
    if ab.mag == 0:
        return a.copy

    ab = ab.norm
    ab *= ap.x * ab.x + ap.y * ab.y
    return a + ab


class Path:
    def __init__(self) -> None:
        self.radius = 20
        self.points: list[py5.Py5Vector] = []

    def add_point(self, x: float, y: float) -> None:
        self.points.append(py5.Py5Vector(x, y))

    def get_start(self) -> py5.Py5Vector:
        return self.points[0]

    def get_end(self) -> py5.Py5Vector:
        return self.points[-1]

    def show(self) -> None:
        py5.stroke(200)
        py5.stroke_weight(self.radius * 2)
        py5.no_fill()
        py5.begin_shape()
        for point in self.points:
            py5.vertex(point.x, point.y)
        py5.end_shape()

        py5.stroke(0)
        py5.stroke_weight(1)
        py5.no_fill()
        py5.begin_shape()
        for point in self.points:
            py5.vertex(point.x, point.y)
        py5.end_shape()


class Vehicle:
    def __init__(self, x: float, y: float, max_speed: float = 4, max_force: float = 0.1) -> None:
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
            future = future.norm * 50
        future += self.position

        target = None
        normal = None
        world_record = float("inf")

        for i in range(len(p.points) - 1):
            a = p.points[i]
            b = p.points[i + 1]
            normal_point = get_normal_point(future, a, b)

            if normal_point.x < a.x or normal_point.x > b.x:
                normal_point = b.copy

            distance = (future - normal_point).mag
            if distance < world_record:
                world_record = distance
                normal = normal_point
                target = normal_point.copy

                direction = b - a
                if direction.mag > 0:
                    direction = direction.norm * 10
                target += direction

        if world_record > p.radius and target is not None:
            self.seek(target)

        if debug and normal is not None and target is not None:
            py5.stroke(0)
            py5.fill(127)
            py5.stroke_weight(1)
            py5.line(self.position.x, self.position.y, future.x, future.y)
            py5.circle(future.x, future.y, 4)

            py5.circle(normal.x, normal.y, 4)
            py5.line(future.x, future.y, normal.x, normal.y)

            if world_record > p.radius:
                py5.fill(255, 0, 0)
            py5.no_stroke()
            py5.circle(target.x, target.y, 8)

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
        if self.position.x > p.get_end().x + self.r:
            self.position.x = p.get_start().x - self.r
            self.position.y = p.get_start().y + (self.position.y - p.get_end().y)

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


def new_path() -> None:
    global path
    path = Path()
    path.add_point(-20, py5.height / 2)
    path.add_point(py5.random(0, py5.width / 2), py5.random(0, py5.height))
    path.add_point(py5.random(py5.width / 2, py5.width), py5.random(0, py5.height))
    path.add_point(py5.width + 20, py5.height / 2)


def setup() -> None:
    global car1, car2
    py5.size(640, 240)
    new_path()
    car1 = Vehicle(0, py5.height / 2, 2, 0.04)
    car2 = Vehicle(0, py5.height / 2, 3, 0.1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    path.show()

    car1.follow(path)
    car2.follow(path)

    car1.run()
    car2.run()

    car1.borders(path)
    car2.borders(path)


def key_pressed() -> None:
    global debug
    if py5.key == " ":
        debug = not debug
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "path_following_####.png"))


def mouse_pressed() -> None:
    new_path()


py5.run_sketch()
