from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SOLVER_ITERATIONS = 20


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = 4
        self.locked = False

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False

    def set(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = self.position.copy

    def apply_force(self, force: py5.Py5Vector) -> None:
        if not self.locked:
            self.acceleration += force

    def update(self) -> None:
        if self.locked:
            self.acceleration *= 0
            self.previous = self.position.copy
            return

        velocity = self.position - self.previous
        current = self.position.copy
        self.position += velocity + self.acceleration
        self.previous = current
        self.acceleration *= 0

    def constrain_to_world(self) -> None:
        x = min(max(self.position.x, 0), py5.width)
        y = min(max(self.position.y, 0), py5.height)
        if x != self.position.x or y != self.position.y:
            self.position = py5.Py5Vector(x, y)
            self.previous = self.position.copy


class Spring:
    def __init__(self, a: Particle, b: Particle) -> None:
        self.a = a
        self.b = b
        self.rest_length = py5.dist(a.position.x, a.position.y, b.position.x, b.position.y)
        self.strength = 0.01

    def update(self) -> None:
        delta = self.b.position - self.a.position
        distance = delta.mag
        if distance == 0:
            return

        diff = (distance - self.rest_length) / distance
        correction = delta * (0.5 * self.strength * diff)

        if not self.a.locked:
            self.a.position += correction
        if not self.b.locked:
            self.b.position -= correction


particles: list[Particle] = []
springs: list[Spring] = []


def setup() -> None:
    py5.size(640, 240)

    particles.append(Particle(200, 25))
    particles.append(Particle(400, 25))
    particles.append(Particle(350, 125))
    particles.append(Particle(400, 225))
    particles.append(Particle(200, 225))
    particles.append(Particle(250, 125))

    springs.append(Spring(particles[0], particles[1]))
    springs.append(Spring(particles[1], particles[2]))
    springs.append(Spring(particles[2], particles[3]))
    springs.append(Spring(particles[3], particles[4]))
    springs.append(Spring(particles[4], particles[5]))
    springs.append(Spring(particles[5], particles[0]))
    springs.append(Spring(particles[5], particles[2]))
    springs.append(Spring(particles[0], particles[3]))
    springs.append(Spring(particles[1], particles[4]))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    gravity = py5.Py5Vector(0, 0.5)
    for particle in particles:
        particle.apply_force(gravity)
        particle.update()

    for _ in range(SOLVER_ITERATIONS):
        for spring in springs:
            spring.update()
        for particle in particles:
            particle.constrain_to_world()

    py5.background(255)
    py5.fill(127)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.begin_shape()
    for particle in particles:
        py5.vertex(particle.position.x, particle.position.y)
    py5.end_shape(py5.CLOSE)

    if py5.is_mouse_pressed:
        particles[0].lock()
        particles[0].set(py5.mouse_x, py5.mouse_y)
        particles[0].unlock()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "soft_body_character_copy_####.png"))


py5.run_sketch()
