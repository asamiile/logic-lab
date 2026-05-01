from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(py5.random(-1, 1), py5.random(-1, 0))
        self.acceleration = py5.Py5Vector(0, 0)
        self.lifespan = 255.0

    def run(self) -> None:
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


class Repeller:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.power = 150

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127)
        py5.circle(self.position.x, self.position.y, 32)

    def repel(self, particle: Particle) -> py5.Py5Vector:
        force = self.position - particle.position
        distance = py5.constrain(force.mag, 5, 50)
        strength = (-1 * self.power) / (distance * distance)
        if force.mag == 0:
            return py5.Py5Vector(0, 0)
        return force.norm * strength


class Emitter:
    def __init__(self, x: float, y: float) -> None:
        self.origin = py5.Py5Vector(x, y)
        self.particles: list[Particle] = []

    def add_particle(self) -> None:
        self.particles.append(Particle(self.origin.x, self.origin.y))

    def apply_force(self, force: py5.Py5Vector) -> None:
        for particle in self.particles:
            particle.apply_force(force)

    def apply_repeller(self, repeller: Repeller) -> None:
        for particle in self.particles:
            force = repeller.repel(particle)
            particle.apply_force(force)

    def run(self) -> None:
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.run()
            if particle.is_dead():
                self.particles.pop(i)


emitter: Emitter
repeller: Repeller


def setup() -> None:
    global emitter, repeller
    py5.size(640, 240)
    emitter = Emitter(py5.width / 2, 60)
    repeller = Repeller(py5.width / 2, 250)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    emitter.add_particle()

    gravity = py5.Py5Vector(0, 0.1)
    emitter.apply_force(gravity)
    emitter.apply_repeller(repeller)
    emitter.run()

    repeller.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_system_with_repeller_####.png"))


py5.run_sketch()
