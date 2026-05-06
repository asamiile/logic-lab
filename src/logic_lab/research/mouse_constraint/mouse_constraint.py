from pathlib import Path

import py5
import pymunk

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
boundaries: list["Boundary"] = []
boxes: list["Box"] = []
mouse_body: pymunk.Body
mouse_joint: pymunk.constraints.DampedSpring


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Box:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.w = w
        self.h = h
        mass = 1.0
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, (w, h)))
        body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(body, (w, h))
        self.shape.elasticity = 0.6
        self.shape.friction = 0.1
        space.add(body, self.shape)

    def show(self) -> None:
        body = self.shape.body
        bx = float(body.position.x)
        by = to_screen_y(float(body.position.y))

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.rect_mode(py5.CENTER)
        py5.push()
        py5.translate(bx, by)
        py5.rotate(-body.angle)
        py5.rect(0, 0, self.w, self.h)
        py5.pop()


class Boundary:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(body, (w, h))
        self.shape.friction = 0.5
        space.add(body, self.shape)

    def show(self) -> None:
        py5.rect_mode(py5.CENTER)
        py5.fill(127)
        py5.no_stroke()
        py5.rect(self.x, self.y, self.w, self.h)


def setup() -> None:
    global space, mouse_body, mouse_joint
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, 0)

    boundaries.append(Boundary(py5.width / 2, py5.height - 5, py5.width, 10))
    boundaries.append(Boundary(py5.width / 2, 5, py5.width, 10))
    boundaries.append(Boundary(5, py5.height / 2, 10, py5.height))
    boundaries.append(Boundary(py5.width - 5, py5.height / 2, 10, py5.height))

    boxes.append(Box(300, py5.height / 2, 48, 48))
    boxes.append(Box(400, py5.height / 2, 48, 48))

    # Static body for mouse constraint
    mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    mouse_body.position = (0, 0)

    # Spring joint to an actual body (not yet selected; updated in mouseDrag)
    mouse_joint = None

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)

    for boundary in boundaries:
        boundary.show()

    for box in boxes:
        box.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mouse_constraint_####.png"))


def mouse_pressed() -> None:
    global mouse_joint

    mouse_body.position = (py5.mouse_x, py5.height - py5.mouse_y)

    # Find shape under mouse
    point_query = space.point_query_nearest(
        (py5.mouse_x, py5.height - py5.mouse_y), 20, pymunk.ShapeFilter()
    )

    if point_query:
        shape = point_query.shape
        body = shape.body

        if body.body_type != pymunk.Body.STATIC:
            # Attach spring constraint
            if mouse_joint:
                space.remove(mouse_joint)
            mouse_joint = pymunk.constraints.DampedSpring(
                mouse_body, body, (0, 0), (0, 0), 0, 50, 0.1
            )
            space.add(mouse_joint)


def mouse_dragged() -> None:
    if mouse_joint:
        mouse_body.position = (py5.mouse_x, py5.height - py5.mouse_y)


def mouse_released() -> None:
    global mouse_joint
    if mouse_joint:
        space.remove(mouse_joint)
        mouse_joint = None


py5.run_sketch()
