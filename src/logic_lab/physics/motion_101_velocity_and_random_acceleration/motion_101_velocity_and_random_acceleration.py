from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.top_speed = 5

    def update(self) -> None:
        angle = py5.random(py5.TWO_PI)
        self.acceleration = py5.Py5Vector(py5.cos(angle), py5.sin(angle))
        self.acceleration *= py5.random(2)

        self.velocity += self.acceleration
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed
        self.position += self.velocity

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        py5.circle(self.position.x, self.position.y, 48)

    def check_edges(self) -> None:
        if self.position.x > py5.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = py5.width

        if self.position.y > py5.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = py5.height


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
        py5.save_frame(str(SCREENSHOT_DIR / "motion_101_velocity_and_random_acceleration_####.png"))


py5.run_sketch()
