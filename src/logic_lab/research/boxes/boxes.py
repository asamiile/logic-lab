from pathlib import Path

import py5
import pymunk

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
boxes: list["Box"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Box:
    def __init__(self, x: float, y: float) -> None:
        self.w = 16
        mass = 1.0
        moment = pymunk.moment_for_box(mass, (self.w, self.w))
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(self.body, (self.w, self.w))
        self.shape.elasticity = 0.0
        self.shape.friction = 0.1
        space.add(self.body, self.shape)

    def show(self) -> None:
        pos = self.body.position
        angle = self.body.angle
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(float(pos.x), to_screen_y(float(pos.y)))
            py5.rotate(-angle)
            py5.square(0, 0, self.w)

    def check_edge(self) -> bool:
        return to_screen_y(float(self.body.position.y)) > py5.height + self.w

    def remove_body(self) -> None:
        space.remove(self.shape, self.body)


def setup() -> None:
    global space
    py5.size(640, 240)
    space = pymunk.Space()
    # Matter.js default gravity is visually much stronger than (0, -1) in pymunk units.
    space.gravity = (0, -900)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    if py5.is_mouse_pressed:
        boxes.append(Box(py5.mouse_x, py5.mouse_y))

    for i in range(len(boxes) - 1, -1, -1):
        box = boxes[i]
        box.show()
        if box.check_edge():
            box.remove_body()
            boxes.pop(i)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "boxes_####.png"))


py5.run_sketch()
