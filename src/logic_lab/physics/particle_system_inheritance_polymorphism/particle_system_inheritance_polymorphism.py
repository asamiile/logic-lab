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


class Confetti(Particle):
    def show(self) -> None:
        angle = py5.remap(self.position.x, 0, py5.width, 0, py5.TWO_PI * 2)

        py5.rect_mode(py5.CENTER)
        py5.fill(127, self.lifespan)
        py5.stroke(0, self.lifespan)
        py5.stroke_weight(2)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(angle)
            py5.square(0, 0, 12)


class Emitter:
    def __init__(self, x: float, y: float) -> None:
        self.origin = py5.Py5Vector(x, y)
        self.particles: list[Particle] = []

    def add_particle(self) -> None:
        if py5.random(1) < 0.5:
            self.particles.append(Particle(self.origin.x, self.origin.y))
        else:
            self.particles.append(Confetti(self.origin.x, self.origin.y))

    def run(self) -> None:
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.run()
            if particle.is_dead():
                self.particles.pop(i)


emitter: Emitter


def setup() -> None:
    global emitter
    py5.size(640, 240)
    emitter = Emitter(py5.width / 2, 20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    emitter.add_particle()
    emitter.run()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_system_inheritance_polymorphism_####.png"))


py5.run_sketch()
