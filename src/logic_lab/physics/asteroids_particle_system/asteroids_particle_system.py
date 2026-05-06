from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

pressed_keys: set[int | str] = set()


class Particle:
    def __init__(self, x: float, y: float, direction: py5.Py5Vector) -> None:
        self.acceleration = py5.Py5Vector(direction.x, direction.y)
        angle = py5.random(py5.TWO_PI)
        self.velocity = py5.Py5Vector(py5.cos(angle), py5.sin(angle))
        self.position = py5.Py5Vector(x, y)
        self.lifespan = 255.0

    def run(self) -> None:
        self.update()
        self.display()

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.lifespan -= 2.0

    def display(self) -> None:
        py5.no_stroke()
        py5.fill(127, 0, 0, self.lifespan)
        py5.ellipse(self.position.x, self.position.y, 12, 12)

    def is_dead(self) -> bool:
        return self.lifespan < 0.0


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def add_particle(self, x: float, y: float, force: py5.Py5Vector) -> None:
        self.particles.append(Particle(x, y, force))

    def run(self) -> None:
        for particle in self.particles:
            particle.run()
        self.particles = [particle for particle in self.particles if not particle.is_dead()]


class Spaceship:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.particle_system = ParticleSystem()
        self.damping = 0.995
        self.top_speed = 6
        self.heading = 0.0
        self.r = 16
        self.thrusting = False

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity *= self.damping
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed
        self.position += self.velocity
        self.acceleration *= 0

        self.particle_system.run()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def turn(self, angle: float) -> None:
        self.heading += angle

    def thrust(self) -> None:
        angle = self.heading - py5.PI / 2
        force = py5.Py5Vector(py5.cos(angle), py5.sin(angle))
        force *= 0.1
        self.apply_force(force)

        exhaust = py5.Py5Vector(force.x, force.y)
        exhaust *= -1
        if exhaust.mag > 0:
            exhaust = exhaust.norm * 5
        self.particle_system.add_particle(self.position.x, self.position.y, exhaust)

        self.thrusting = True

    def wrap_edges(self) -> None:
        buffer = self.r * 2
        if self.position.x > py5.width + buffer:
            self.position.x = -buffer
        elif self.position.x < -buffer:
            self.position.x = py5.width + buffer

        if self.position.y > py5.height + buffer:
            self.position.y = -buffer
        elif self.position.y < -buffer:
            self.position.y = py5.height + buffer

    def display(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.rect_mode(py5.CENTER)

        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(self.heading)

            if self.thrusting:
                py5.fill(255, 0, 0)
            else:
                py5.fill(175)
            py5.rect(-self.r / 2, self.r, self.r / 3, self.r / 2)
            py5.rect(self.r / 2, self.r, self.r / 3, self.r / 2)

            py5.fill(175)
            py5.begin_shape()
            py5.vertex(-self.r, self.r)
            py5.vertex(0, -self.r)
            py5.vertex(self.r, self.r)
            py5.end_shape(py5.CLOSE)

        self.thrusting = False


ship: Spaceship


def setup() -> None:
    global ship
    py5.size(640, 240)
    ship = Spaceship()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    ship.update()
    ship.wrap_edges()
    ship.display()

    py5.fill(0)
    py5.no_stroke()
    py5.text("left right arrows to turn, up to thrust", 10, py5.height - 5)

    if py5.LEFT in pressed_keys:
        ship.turn(-0.03)
    elif py5.RIGHT in pressed_keys:
        ship.turn(0.03)
    elif py5.UP in pressed_keys:
        ship.thrust()


def key_pressed() -> None:
    pressed_keys.add(py5.key_code)
    if py5.key:
        pressed_keys.add(str(py5.key).lower())

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "asteroids_particle_system_####.png"))


def key_released() -> None:
    pressed_keys.discard(py5.key_code)
    if py5.key:
        pressed_keys.discard(str(py5.key).lower())


py5.run_sketch()
