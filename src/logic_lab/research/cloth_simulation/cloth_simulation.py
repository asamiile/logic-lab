from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
COLS = 65
ROWS = 20
SPACING = 10
SPRING_STRENGTH = 0.2
SOLVER_ITERATIONS = 10
DRAG = 0.02
SIMULATION_STEPS_PER_FRAME = 6
TIME_SCALE = 1.0


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.locked = False

    def lock(self) -> None:
        self.locked = True

    def apply_force(self, force: py5.Py5Vector) -> None:
        if not self.locked:
            self.acceleration += force

    def update(self) -> None:
        if self.locked:
            self.acceleration *= 0
            self.previous = self.position.copy
            return

        velocity = self.position - self.previous
        velocity *= 1.0 - DRAG
        current = self.position.copy
        self.position += velocity + self.acceleration
        self.previous = current
        self.acceleration *= 0


class Spring:
    def __init__(self, a: Particle, b: Particle) -> None:
        self.a = a
        self.b = b
        self.rest_length = SPACING
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
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.line(self.a.position.x, self.a.position.y, self.b.position.x, self.b.position.y)


particles: list[list[Particle]] = [[None for _ in range(ROWS)] for _ in range(COLS)]  # type: ignore[list-item]
springs: list[Spring] = []


def setup() -> None:
    py5.size(640, 240)

    x = 0
    for i in range(COLS):
        y = 0
        for j in range(ROWS):
            p = Particle(x, y)
            particles[i][j] = p
            y += SPACING
        x += SPACING

    for i in range(COLS):
        for j in range(ROWS):
            a = particles[i][j]
            if i != COLS - 1:
                b1 = particles[i + 1][j]
                springs.append(Spring(a, b1))
            if j != ROWS - 1:
                b2 = particles[i][j + 1]
                springs.append(Spring(a, b2))

    for i in range(0, COLS, 4):
        particles[i][0].lock()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    gravity = py5.Py5Vector(0, 1 * TIME_SCALE)
    for _ in range(SIMULATION_STEPS_PER_FRAME):
        for i in range(COLS):
            for j in range(ROWS):
                p = particles[i][j]
                p.apply_force(gravity)
                p.update()

        for _ in range(SOLVER_ITERATIONS):
            for spring in springs:
                spring.update()

    for spring in springs:
        spring.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "cloth_simulation_####.png"))


py5.run_sketch()
