from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
DRAG = 0.01

particles: list["Particle"] = []
attractor: "Attractor"
behaviors: list["AttractionBehavior"] = []


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

        velocity = (self.position - self.previous) * (1 - DRAG)
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
        py5.fill(127)
        py5.stroke(0)
        py5.circle(self.position.x, self.position.y, self.r * 2)


class Attractor(Particle):
    def show(self) -> None:
        py5.fill(0)
        py5.no_stroke()
        py5.circle(self.position.x, self.position.y, self.r * 2)


class AttractionBehavior:
    def __init__(self, source: Particle, radius: float, strength: float) -> None:
        self.source = source
        self.radius = radius
        self.strength = strength

    def apply(self, targets: list[Particle]) -> None:
        for target in targets:
            if target is self.source:
                continue

            delta = self.source.position - target.position
            distance = delta.mag
            if distance == 0 or distance > self.radius:
                continue

            # Smooth falloff within radius; negative strength means repulsion.
            scale = (1 - distance / self.radius) * self.strength
            force = delta.norm * scale
            target.apply_force(force)


def setup() -> None:
    global attractor
    py5.size(640, 240)

    for _ in range(50):
        particle = Particle(py5.random(py5.width), py5.random(py5.height), 4)
        particles.append(particle)
        behaviors.append(AttractionBehavior(particle, particle.r * 2, -2))

    attractor = Attractor(py5.width / 2, py5.height / 2, 16)
    particles.append(attractor)
    behaviors.append(AttractionBehavior(attractor, py5.width, 0.1))
    behaviors.append(AttractionBehavior(attractor, attractor.r + 4, -5))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    for behavior in behaviors:
        behavior.apply(particles)

    for particle in particles:
        particle.update()
        particle.constrain_to_world()

    attractor.show()
    for particle in particles:
        if particle is not attractor:
            particle.show()

    if py5.is_mouse_pressed:
        attractor.lock()
        attractor.set(py5.mouse_x, py5.mouse_y)
    else:
        attractor.unlock()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "attraction_behaviors_####.png"))


py5.run_sketch()
