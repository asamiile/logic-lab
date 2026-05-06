from pathlib import Path

import py5
import pymunk

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
boxes: list["Box"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Box:
    W = 16

    def __init__(self, x: float, y: float) -> None:
        mass = 1.0
        size = (self.W, self.W)
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(body, size)
        self.shape.friction = 0.3
        self.shape.elasticity = 0.5
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


def setup() -> None:
    global space
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -1000)

    ground = pymunk.Segment(space.static_body, (0, 5), (py5.width, 5), 5)
    ground.friction = 0.5
    ground.elasticity = 1.0
    space.add(ground)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    if py5.is_mouse_pressed:
        boxes.append(Box(py5.mouse_x, py5.mouse_y))

    py5.stroke(0)
    py5.stroke_weight(10)
    py5.no_fill()
    py5.line(0, to_screen_y(5), py5.width, to_screen_y(5))

    for box in boxes:
        box.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "boxes_exercise_####.png"))


py5.run_sketch()
