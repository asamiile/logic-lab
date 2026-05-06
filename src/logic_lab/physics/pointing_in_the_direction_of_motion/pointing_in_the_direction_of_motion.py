from math import atan2
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.top_speed = 4

    def update(self) -> None:
        mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
        direction = mouse - self.position

        if direction.mag > 0:
            self.acceleration = direction.norm * 0.5
        else:
            self.acceleration *= 0

        self.velocity += self.acceleration
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed
        self.position += self.velocity

    def check_edges(self) -> None:
        if self.position.x > py5.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = py5.width

        if self.position.y > py5.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = py5.height

    def show(self) -> None:
        angle = atan2(self.velocity.y, self.velocity.x)

        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        py5.rect_mode(py5.CENTER)

        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(angle)
            py5.rect(0, 0, 30, 10)


mover: Mover


def setup() -> None:
    global mover
    py5.size(640, 240)
    mover = Mover()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    mover.update()
    mover.check_edges()
    mover.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pointing_in_the_direction_of_motion_####.png"))


py5.run_sketch()
