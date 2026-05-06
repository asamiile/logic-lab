from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

pursuer: "Vehicle"
target: "Target"


def limit_vector(v: py5.Py5Vector, max_val: float) -> py5.Py5Vector:
    mag_sq = v.x * v.x + v.y * v.y
    if mag_sq > max_val * max_val:
        scale = max_val / mag_sq**0.5
        return py5.Py5Vector(v.x * scale, v.y * scale)
    return v


class Vehicle:
    def __init__(self, x: float, y: float) -> None:
        self.pos = py5.Py5Vector(x, y)
        self.vel = py5.Py5Vector(0, 0)
        self.acc = py5.Py5Vector(0, 0)
        self.max_speed = 8.0
        self.max_force = 0.25
        self.r = 8.0

    def seek(self, target: py5.Py5Vector) -> py5.Py5Vector:
        force = target - self.pos
        force = force.norm * self.max_speed - self.vel
        return limit_vector(force, self.max_force)

    def flee(self, target: py5.Py5Vector) -> py5.Py5Vector:
        return self.seek(target) * -1

    def pursue(self, vehicle: "Vehicle") -> py5.Py5Vector:
        predicted = vehicle.pos + vehicle.vel * 10
        py5.fill(175)
        py5.stroke(0)
        py5.circle(predicted.x, predicted.y, 16)
        return self.seek(predicted)

    def evade(self, vehicle: "Vehicle") -> py5.Py5Vector:
        return self.pursue(vehicle) * -1

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acc += force

    def update(self) -> None:
        self.vel += self.acc
        self.vel = limit_vector(self.vel, self.max_speed)
        self.pos += self.vel
        self.acc *= 0

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        with py5.push_matrix():
            py5.translate(self.pos.x, self.pos.y)
            py5.rotate(self.vel.heading)
            py5.triangle(-self.r, -self.r / 2, -self.r, self.r / 2, self.r, 0)

    def edges(self) -> None:
        if self.pos.x > py5.width + self.r:
            self.pos.x = -self.r
        elif self.pos.x < -self.r:
            self.pos.x = py5.width + self.r
        if self.pos.y > py5.height + self.r:
            self.pos.y = -self.r
        elif self.pos.y < -self.r:
            self.pos.y = py5.height + self.r


class Target(Vehicle):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.r = 16.0
        self.vel = py5.Py5Vector.random(dim=2) * 5

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        with py5.push_matrix():
            py5.translate(self.pos.x, self.pos.y)
            py5.circle(0, 0, self.r * 2)


def setup() -> None:
    global pursuer, target
    py5.size(640, 240)
    pursuer = Vehicle(100, 100)
    target = Target(500, 200)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global target
    py5.background(255)

    steering = pursuer.pursue(target)
    pursuer.apply_force(steering)

    d = (pursuer.pos - target.pos).mag
    if d < pursuer.r + target.r:
        target = Target(py5.random(py5.width), py5.random(py5.height))
        pursuer.pos = py5.Py5Vector(py5.width / 2, py5.height / 2)

    pursuer.update()
    pursuer.show()

    target.edges()
    target.update()
    target.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pursuit_behavior_####.png"))


py5.run_sketch()
