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
        mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)

        # Step 1: Compute direction
        direction = mouse - self.position
        # Step 2: Normalize
        direction = direction.norm
        # Step 3: Scale
        direction *= 0.2
        # Step 4: Accelerate
        self.acceleration = direction

        self.velocity += self.acceleration
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed
        self.position += self.velocity

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        py5.circle(self.position.x, self.position.y, 48)


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
        py5.save_frame(str(SCREENSHOT_DIR / "accelerating_towards_the_mouse_####.png"))


py5.run_sketch()
