from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SOLVER_ITERATIONS = 20
SPRING_STRENGTH = 0.001


class Particle:
    def __init__(self, x: float, y: float, r: float = 2) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = r
        self.locked = False

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False

    def set(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = self.position.copy

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

    def show(self) -> None:
        py5.fill(252, 238, 33)
        py5.stroke_weight(1)
        py5.circle(self.position.x, self.position.y, self.r * 12)
        py5.stroke_weight(self.r * 4)
        py5.point(self.position.x, self.position.y)


class Spring:
    def __init__(self, a: Particle, b: Particle) -> None:
        self.a = a
        self.b = b
        self.rest_length = py5.dist(a.position.x, a.position.y, b.position.x, b.position.y)
        self.strength = SPRING_STRENGTH

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

    def show(self) -> None:
        py5.stroke_weight(1)
        py5.stroke(0, 127)
        py5.line(self.a.position.x, self.a.position.y, self.b.position.x, self.b.position.y)


particles: list[Particle] = []
eyes: list[Particle] = []
springs: list[Spring] = []
show_springs = False


def setup() -> None:
    py5.size(640, 240)

    particles.extend(
        [
            Particle(200, 25),
            Particle(250, 25),
            Particle(300, 25),
            Particle(350, 25),
            Particle(400, 25),
            Particle(350, 125),
            Particle(400, 225),
            Particle(350, 225),
            Particle(300, 225),
            Particle(250, 225),
            Particle(200, 225),
            Particle(250, 125),
        ]
    )

    eyes.extend([Particle(275, 75), Particle(325, 75), Particle(250, -25), Particle(350, -25)])

    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            springs.append(Spring(particles[i], particles[j]))

    for p in particles:
        springs.append(Spring(p, eyes[0]))
        springs.append(Spring(p, eyes[1]))

    springs.append(Spring(eyes[2], particles[1]))
    springs.append(Spring(eyes[3], particles[3]))
    springs.append(Spring(eyes[2], particles[3]))
    springs.append(Spring(eyes[3], particles[1]))
    springs.append(Spring(eyes[2], particles[0]))
    springs.append(Spring(eyes[3], particles[4]))
    springs.append(Spring(eyes[3], particles[2]))
    springs.append(Spring(eyes[2], particles[2]))
    springs.append(Spring(eyes[2], eyes[3]))
    springs.append(Spring(eyes[0], eyes[3]))
    springs.append(Spring(eyes[0], eyes[2]))
    springs.append(Spring(eyes[1], eyes[2]))
    springs.append(Spring(eyes[1], eyes[3]))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    for p in particles:
        p.update()
        p.constrain_to_world()
    for eye in eyes:
        eye.update()
        eye.constrain_to_world()

    for _ in range(SOLVER_ITERATIONS):
        for spring in springs:
            spring.update()
        for p in particles:
            p.constrain_to_world()
        for eye in eyes:
            eye.constrain_to_world()

    py5.background(255)

    py5.stroke(112, 50, 126)
    if show_springs:
        py5.stroke(112, 50, 126, 100)

    py5.stroke_weight(4)
    py5.line(particles[1].position.x, particles[1].position.y, eyes[2].position.x, eyes[2].position.y)
    py5.line(particles[3].position.x, particles[3].position.y, eyes[3].position.x, eyes[3].position.y)
    py5.stroke_weight(16)
    py5.point(eyes[2].position.x, eyes[2].position.y)
    py5.point(eyes[3].position.x, eyes[3].position.y)

    py5.fill(45, 197, 244)
    if show_springs:
        py5.fill(45, 197, 244, 100)
    py5.stroke_weight(2)
    py5.begin_shape()
    for p in particles:
        py5.vertex(p.position.x, p.position.y)
    py5.end_shape(py5.CLOSE)

    eyes[0].show()
    eyes[1].show()

    if show_springs:
        for spring in springs:
            spring.show()

    if py5.is_mouse_pressed:
        particles[0].lock()
        particles[0].set(py5.mouse_x, py5.mouse_y)
        particles[0].unlock()


def key_pressed() -> None:
    global show_springs
    if py5.key == " ":
        show_springs = not show_springs
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "soft_body_character_enhanced_####.png"))


py5.run_sketch()
