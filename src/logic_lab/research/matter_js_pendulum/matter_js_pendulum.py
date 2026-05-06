from pathlib import Path

import py5
import pymunk

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
pendulum: "Pendulum"


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Pendulum:
    def __init__(self, x: float, y: float, length: float) -> None:
        self.r = 12
        self.len = length

        # Anchor: static circle at screen (x, y)
        anchor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        anchor_body.position = (x, py5.height - y)
        self.anchor_shape = pymunk.Circle(anchor_body, self.r)

        # Bob: dynamic circle starting directly right of anchor at exactly len distance
        bob_body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, self.r))
        bob_body.position = (x + length, py5.height - y)
        self.bob_shape = pymunk.Circle(bob_body, self.r)
        self.bob_shape.elasticity = 0.6

        # Prevent anchor and bob from colliding with each other
        no_collide = pymunk.ShapeFilter(group=1)
        self.anchor_shape.filter = no_collide
        self.bob_shape.filter = no_collide

        space.add(anchor_body, self.anchor_shape, bob_body, self.bob_shape)

        # Arm: fixed-length rigid constraint (SlideJoint with min=max=len)
        self.arm = pymunk.constraints.SlideJoint(
            anchor_body, bob_body, (0, 0), (0, 0), self.len, self.len
        )
        space.add(self.arm)

    def show(self) -> None:
        anchor_pos = self.anchor_shape.body.position
        bob_pos = self.bob_shape.body.position

        ax = float(anchor_pos.x)
        ay = to_screen_y(float(anchor_pos.y))
        bx = float(bob_pos.x)
        by = to_screen_y(float(bob_pos.y))

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)

        # Arm line
        py5.line(ax, ay, bx, by)

        # Anchor circle with rotation indicator
        py5.push()
        py5.translate(ax, ay)
        py5.rotate(-self.anchor_shape.body.angle)
        py5.circle(0, 0, self.r * 2)
        py5.line(0, 0, self.r, 0)
        py5.pop()

        # Bob circle with rotation indicator
        py5.push()
        py5.translate(bx, by)
        py5.rotate(-self.bob_shape.body.angle)
        py5.circle(0, 0, self.r * 2)
        py5.line(0, 0, self.r, 0)
        py5.pop()


def setup() -> None:
    global space, pendulum
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -1000)

    pendulum = Pendulum(py5.width / 2, 10, 100)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    space.step(1 / 60)
    pendulum.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "matter_js_pendulum_####.png"))


py5.run_sketch()
