from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
boxes: list["Box"] = []
boundaries: list["Boundary"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Box:
    def __init__(self, x: float, y: float) -> None:
        self.w = py5.random(8, 16)
        self.h = py5.random(8, 16)
        mass = 1.0
        size = (self.w, self.h)
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        body.position = (x, py5.height - y)
        # Matter.js velocity is px/frame; pymunk is px/s → multiply by 60
        body.velocity = (py5.random(-5, 5) * 60, 0)
        body.angular_velocity = 0.1 * 60
        self.shape = pymunk.Poly.create_box(body, size)
        # elasticity=1.0 on boundary, so effective = 0.6 * 1.0 = 0.6 (matches restitution: 0.6)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.1
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
        # pymunk y-up: box fell off screen when y < -w
        return self.shape.body.position.y < -self.w

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

    if py5.random(1) < 0.1:
        boxes.append(Box(py5.width / 2, 50))

    for i in range(len(boxes) - 1, -1, -1):
        boxes[i].show()
        if boxes[i].check_edge():
            boxes[i].remove_body()
            boxes.pop(i)

    for boundary in boundaries:
        boundary.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "boxes_and_boundaries_####.png"))


py5.run_sketch()
