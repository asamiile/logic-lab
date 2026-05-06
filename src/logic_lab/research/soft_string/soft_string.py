from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SOLVER_ITERATIONS = 30


class Particle:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = r
        self.locked = False

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False

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

    def constrain_to_world(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        if self.position.x < min_x:
            self.position.x = min_x
        elif self.position.x > max_x:
            self.position.x = max_x

        if self.position.y < min_y:
            self.position.y = min_y
        elif self.position.y > max_y:
            self.position.y = max_y

    def show(self) -> None:
        py5.fill(127)
        py5.stroke(0)
        py5.circle(self.position.x, self.position.y, self.r * 2)


class Spring:
    def __init__(self, a: Particle, b: Particle, rest_length: float, strength: float) -> None:
        self.a = a
        self.b = b
        self.rest_length = rest_length
        self.strength = strength

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

    spacing = 10
    total = 20
    for i in range(total):
        particle = Particle(py5.width / 2 + i * spacing, 0, 16)
        particles.append(particle)

    for i in range(total - 1):
        springs.append(Spring(particles[i], particles[i + 1], spacing, 0.2))

    particles[0].lock()
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
            particle.constrain_to_world(0, 0, py5.width, py5.height - particle.r)

    py5.background(255)
    py5.stroke(0)
    py5.no_fill()
    py5.begin_shape()
    for particle in particles:
        py5.vertex(particle.position.x, particle.position.y)
    py5.end_shape()

    particles[-1].show()

    if py5.is_mouse_pressed:
        tail = particles[-1]
        tail.lock()
        tail.position = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
        tail.previous = tail.position.copy
        tail.unlock()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "soft_string_####.png"))


py5.run_sketch()
