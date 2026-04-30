from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(py5.random(-1, 1), py5.random(-2, 0))
        self.acceleration = py5.Py5Vector(0, 0)
        self.lifespan = 255.0

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.lifespan -= 2.0
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke(0, self.lifespan)
        py5.fill(0, self.lifespan)
        py5.circle(self.position.x, self.position.y, 8)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def is_dead(self) -> bool:
        return self.lifespan < 0


particle: Particle


def setup() -> None:
    global particle
    py5.size(640, 240)
    particle = Particle(py5.width / 2, 10)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global particle
    py5.background(255)

    particle.update()
    particle.show()

    gravity = py5.Py5Vector(0, 0.1)
    particle.apply_force(gravity)

    if particle.is_dead():
        particle = Particle(py5.width / 2, 20)
        print("Particle dead!")


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "single_particle_####.png"))


py5.run_sketch()
