from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
OSCILLATOR_COUNT = 10


class Oscillator:
    def __init__(self) -> None:
        self.angle = py5.Py5Vector(dim=2)
        self.angle_velocity = py5.Py5Vector(py5.random(-0.05, 0.05), py5.random(-0.05, 0.05))
        self.amplitude = py5.Py5Vector(
            py5.random(20, py5.width / 2),
            py5.random(20, py5.height / 2),
        )

    def update(self) -> None:
        self.angle += self.angle_velocity

    def show(self) -> None:
        x = py5.sin(self.angle.x) * self.amplitude.x
        y = py5.sin(self.angle.y) * self.amplitude.y

        with py5.push_matrix():
            py5.translate(py5.width / 2, py5.height / 2)
            py5.stroke(0)
            py5.stroke_weight(2)
            py5.fill(127)
            py5.line(0, 0, x, y)
            py5.circle(x, y, 32)


oscillators: list[Oscillator]


def setup() -> None:
    global oscillators
    py5.size(640, 240)
    oscillators = [Oscillator() for _ in range(OSCILLATOR_COUNT)]
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    for oscillator in oscillators:
        oscillator.update()
        oscillator.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "oscillator_objects_####.png"))


py5.run_sketch()
