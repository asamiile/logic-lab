from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Particle:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(0, 0)
        self.position = py5.Py5Vector(x, y)
        self.lifespan = 255.0
        self.r = r

    def run(self) -> None:
        self.update()
        self.show()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.velocity *= 0.95
        self.lifespan -= 2.0

    def show(self) -> None:
        py5.stroke(0)
        py5.fill(0)
        py5.rect_mode(py5.CENTER)
        py5.rect(self.position.x, self.position.y, self.r, self.r)

    def is_dead(self) -> bool:
        return self.lifespan < 0.0


class ParticleSystem:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.particles: list[Particle] = []
        rows = 10
        cols = 10
        for i in range(rows * cols):
            self.add_particle(x + (i % cols) * r, y + (i // rows) * r, r)

    def add_particle(self, x: float, y: float, r: float) -> None:
        self.particles.append(Particle(x, y, r))

    def show(self) -> None:
        for particle in self.particles:
            particle.show()

    def shatter(self) -> None:
        for particle in self.particles:
            angle = py5.random(py5.TWO_PI)
            force = py5.Py5Vector(py5.cos(angle), py5.sin(angle)) * 10
            particle.apply_force(force)

    def update(self) -> None:
        for particle in self.particles:
            particle.update()


block: ParticleSystem


def setup() -> None:
    global block
    py5.size(640, 240)
    block = ParticleSystem(270, 70, 10)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    block.show()
    block.update()


def mouse_pressed() -> None:
    block.shatter()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_shatter_####.png"))


py5.run_sketch()
