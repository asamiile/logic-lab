from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
shapes: list["CustomShape"] = []
boundaries: list["Boundary"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class CustomShape:
    # Original Matter.js vertices are y-down; negate y for pymunk y-up
    VERTICES = [(-10, 10), (20, 15), (15, 0), (0, -10), (-20, -15)]

    def __init__(self, x: float, y: float) -> None:
        mass = 1.0
        body = pymunk.Body(mass, pymunk.moment_for_poly(mass, self.VERTICES))
        body.position = (x, py5.height - y)
        body.velocity = (py5.random(-5, 5) * 60, 0)
        body.angular_velocity = 0.1 * 60
        self.shape = pymunk.Poly(body, self.VERTICES)
        self.shape.elasticity = 0.2
        self.shape.friction = 0.3
        space.add(body, self.shape)

    def show(self) -> None:
        body = self.shape.body
        verts = [body.local_to_world(v) for v in self.shape.get_vertices()]
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.begin_shape()
        for v in verts:
            py5.vertex(float(v.x), to_screen_y(float(v.y)))
        py5.end_shape(py5.CLOSE)

    def check_edge(self) -> bool:
        return self.shape.body.position.y < -100

    def remove_body(self) -> None:
        space.remove(self.shape.body, self.shape)


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
        shapes.append(CustomShape(py5.width / 2, 50))

    for i in range(len(shapes) - 1, -1, -1):
        shapes[i].show()
        if shapes[i].check_edge():
            shapes[i].remove_body()
            shapes.pop(i)

    for boundary in boundaries:
        boundary.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "polygon_shapes_####.png"))


py5.run_sketch()
