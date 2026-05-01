from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

SLEEPER_SIZE = 5
TRAIN_W = 64


def draw_train(x: float, y: float) -> None:
    py5.push()
    py5.translate(x, y)
    # body
    py5.fill(220, 80, 60)
    py5.stroke(0)
    py5.stroke_weight(1)
    py5.rect(0, 16, TRAIN_W, 32)
    # cab
    py5.fill(180, 60, 40)
    py5.rect(4, 4, 28, 16)
    # window
    py5.fill(180, 220, 255)
    py5.rect(8, 8, 16, 8)
    # chimney
    py5.fill(60, 60, 60)
    py5.rect(10, 0, 8, 6)
    # wheels
    py5.fill(40)
    py5.circle(12, 48, 16)
    py5.circle(44, 48, 16)
    py5.pop()


class CodingTrain:
    def __init__(self, starting_position: py5.Py5Vector) -> None:
        self.position = py5.Py5Vector(starting_position.x, starting_position.y)
        self.velocity = py5.Py5Vector(1, 0)
        self.acceleration = py5.Py5Vector(0, 0)

    def update(self) -> None:
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.mag > 25:
            self.velocity = self.velocity.norm * 25
        if self.velocity.x <= 0:
            self.velocity.x = 0
            self.acceleration.x = 0

        if self.position.x > py5.width:
            self.position.x = -TRAIN_W
        if self.position.x < -TRAIN_W:
            self.position.x = py5.width

    def show(self) -> None:
        draw_train(self.position.x, self.position.y)

    def on_key_pressed(self) -> None:
        if py5.key_code == py5.UP:
            self.acceleration.x += 0.1
        if py5.key_code == py5.DOWN:
            self.acceleration.x -= 0.1


coding_train: CodingTrain


def setup() -> None:
    global coding_train
    py5.size(640, 240)
    starting_position = py5.Py5Vector(
        py5.width / 2 - TRAIN_W / 2,
        py5.height / 2 - TRAIN_W - 1,
    )
    coding_train = CodingTrain(starting_position)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    # railroad
    py5.fill(0)
    py5.line(0, py5.height / 2, py5.width, py5.height / 2)
    i = 0
    while i < py5.width - SLEEPER_SIZE:
        py5.rect(i, py5.height / 2, SLEEPER_SIZE, SLEEPER_SIZE / 2)
        i += SLEEPER_SIZE * 3

    coding_train.update()
    coding_train.show()


def key_pressed() -> None:
    coding_train.on_key_pressed()
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "accelerate_and_decelerate_####.png"))


py5.run_sketch()
