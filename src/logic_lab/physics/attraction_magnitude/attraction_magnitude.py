from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.top_speed = 5
        self.diameter = 48

    def update(self) -> None:
        mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)

        direction = mouse - self.position
        new_magnitude = py5.remap(
            direction.mag, 0, max(py5.width, py5.height), 0, 0.2
        )
        direction = direction.norm * new_magnitude
        self.acceleration = direction

        self.velocity += self.acceleration
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed
        self.position += self.velocity

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        py5.circle(self.position.x, self.position.y, self.diameter)


mover: Mover


def setup() -> None:
    global mover
    py5.size(640, 240)
    mover = Mover()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    mover.update()
    mover.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "attraction_magnitude_####.png"))


py5.run_sketch()
