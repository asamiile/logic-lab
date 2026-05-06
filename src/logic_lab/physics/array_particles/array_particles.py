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


particles: list[Particle] = []


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    particles.append(Particle(py5.width / 2, 20))

    for i in range(len(particles) - 1, -1, -1):
        particle = particles[i]
        particle.run()
        if particle.is_dead():
            particles.pop(i)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "array_particles_####.png"))


py5.run_sketch()
