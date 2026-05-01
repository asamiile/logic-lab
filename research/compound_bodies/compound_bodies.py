from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
lollipops: list["Lollipop"] = []
boundaries: list["Boundary"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Lollipop:
    def __init__(self, x: float, y: float) -> None:
        self.w = 24
        self.h = 4
        self.r = 8
        mass = 1.0
        # Compound moment: stick at origin + circle at (w/2, 0) via parallel axis theorem
        moment = pymunk.moment_for_box(mass, (self.w, self.h)) + pymunk.moment_for_circle(
            mass, 0, self.r, offset=(self.w / 2, 0)
        )
        body = pymunk.Body(mass * 2, moment)
        body.position = (x, py5.height - y)
        body.velocity = (py5.random(-5, 5) * 60, 0)
        body.angular_velocity = 0.1 * 60

        # Stick centered at body origin; candy circle at right end of stick
        self.stick_shape = pymunk.Poly.create_box(body, (self.w, self.h))
        self.circle_shape = pymunk.Circle(body, self.r, offset=(self.w / 2, 0))
        for shape in (self.stick_shape, self.circle_shape):
            shape.elasticity = 1.0
            shape.friction = 0.3
        space.add(body, self.stick_shape, self.circle_shape)

    def show(self) -> None:
        body = self.stick_shape.body

        # Stick: transform each vertex to world coords then to screen
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(1)
        py5.begin_shape()
        for v in self.stick_shape.get_vertices():
            wv = body.local_to_world(v)
            py5.vertex(float(wv.x), to_screen_y(float(wv.y)))
        py5.end_shape(py5.CLOSE)

        # Candy circle: center in world space
        center = body.local_to_world((self.w / 2, 0))
        py5.fill(200)
        py5.no_stroke()
        py5.circle(float(center.x), to_screen_y(float(center.y)), self.r * 2)

    def check_edge(self) -> bool:
        return self.stick_shape.body.position.y < -(self.h * 2)

    def remove_body(self) -> None:
        body = self.stick_shape.body
        space.remove(body, self.stick_shape, self.circle_shape)


class Boundary:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(body, (w, h))
        self.shape.elasticity = 1.0
        self.shape.friction = 0.5
        space.add(body, self.shape)

    def show(self) -> None:
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.rect(self.x, self.y, self.w, self.h)


def setup() -> None:
    global space
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -1000)

    boundaries.append(Boundary(py5.width / 4, py5.height - 5, py5.width / 2 - 50, 10))
    boundaries.append(Boundary(3 * py5.width / 4, py5.height - 50, py5.width / 2 - 50, 10))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    if py5.random(1) < 0.025:
        lollipops.append(Lollipop(py5.width / 2, 50))

    for i in range(len(lollipops) - 1, -1, -1):
        lollipops[i].show()
        if lollipops[i].check_edge():
            lollipops[i].remove_body()
            lollipops.pop(i)

    for boundary in boundaries:
        boundary.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "compound_bodies_####.png"))


py5.run_sketch()
