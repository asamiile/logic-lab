from math import cos, sin, pi
from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

wanderer: "Vehicle"
debug = True


def limit_vector(v: py5.Py5Vector, max_val: float) -> py5.Py5Vector:
    mag_sq = v.x * v.x + v.y * v.y
    if mag_sq > max_val * max_val:
        scale = max_val / mag_sq ** 0.5
        return py5.Py5Vector(v.x * scale, v.y * scale)
    return v


class Vehicle:
    def __init__(self, x: float, y: float) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(0, 0)
        self.position = py5.Py5Vector(x, y)
        self.r = 6.0
        self.wander_theta = 0.0
        self.max_speed = 2.0
        self.max_force = 0.05

    def run(self) -> None:
        self.update()
        self.borders()
        self.show()

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def wander(self) -> None:
        wander_r = 25.0
        wander_d = 80.0
        change = 0.3
        self.wander_theta += py5.random(-change, change)

        if self.velocity.mag > 0:
            circle_pos = self.velocity.norm * wander_d + self.position
        else:
            circle_pos = py5.Py5Vector(wander_d, 0) + self.position

        h = self.velocity.heading
        circle_offset = py5.Py5Vector(
            wander_r * cos(self.wander_theta + h),
            wander_r * sin(self.wander_theta + h),
        )
        target = circle_pos + circle_offset
        self.seek(target)

        if debug:
            self.draw_wander_stuff(self.position, circle_pos, target, wander_r)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def seek(self, target: py5.Py5Vector) -> None:
        desired = target - self.position
        if desired.mag > 0:
            desired = desired.norm * self.max_speed
        steer = limit_vector(desired - self.velocity, self.max_force)
        self.apply_force(steer)

    def show(self) -> None:
        theta = self.velocity.heading + pi / 2
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(theta)
            py5.begin_shape()
            py5.vertex(0, -self.r * 2)
            py5.vertex(-self.r, self.r * 2)
            py5.vertex(self.r, self.r * 2)
            py5.end_shape(py5.CLOSE)

    def borders(self) -> None:
        r = self.r
        if self.position.x < -r:
            self.position.x = py5.width + r
        if self.position.y < -r:
            self.position.y = py5.height + r
        if self.position.x > py5.width + r:
            self.position.x = -r
        if self.position.y > py5.height + r:
            self.position.y = -r

    def draw_wander_stuff(
        self,
        location: py5.Py5Vector,
        circle_pos: py5.Py5Vector,
        target: py5.Py5Vector,
        rad: float,
    ) -> None:
        py5.stroke(0)
        py5.no_fill()
        py5.stroke_weight(1)
        py5.circle(circle_pos.x, circle_pos.y, rad * 2)
        py5.circle(target.x, target.y, 4)
        py5.line(location.x, location.y, circle_pos.x, circle_pos.y)
        py5.line(circle_pos.x, circle_pos.y, target.x, target.y)


def setup() -> None:
    global wanderer
    py5.size(640, 240)
    wanderer = Vehicle(py5.width / 2, py5.height / 2)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    wanderer.wander()
    wanderer.run()


def mouse_pressed() -> None:
    global debug
    debug = not debug


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "wander_behavior_####.png"))


py5.run_sketch()
