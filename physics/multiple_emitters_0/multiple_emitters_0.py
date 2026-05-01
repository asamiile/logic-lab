from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(py5.random(-1, 1), py5.random(-1, 0))
        self.lifespan = 255.0

    def run(self) -> None:
        gravity = py5.Py5Vector(0, 0.05)
        self.apply_force(gravity)
        self.update()
        self.show()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.lifespan -= 2
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke(0, self.lifespan)
        py5.stroke_weight(2)
        py5.fill(127, self.lifespan)
        py5.circle(self.position.x, self.position.y, 8)

    def is_dead(self) -> bool:
        return self.lifespan < 0.0


class Emitter:
    def __init__(self, x: float, y: float) -> None:
        self.origin = py5.Py5Vector(x, y)
        self.particles: list[Particle] = []

    def add_particle(self) -> None:
        self.particles.append(Particle(self.origin.x, self.origin.y))

    def run(self) -> None:
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.run()
            if particle.is_dead():
                self.particles.pop(i)


emitters: list[Emitter] = []


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    for emitter in emitters:
        emitter.run()
        emitter.add_particle()


def mouse_pressed() -> None:
    emitters.append(Emitter(py5.mouse_x, py5.mouse_y))


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "multiple_emitters_0_####.png"))


py5.run_sketch()
