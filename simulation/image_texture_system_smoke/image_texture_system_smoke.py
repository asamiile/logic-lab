from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

emitter: "Emitter"
texture: py5.Py5Graphics


def random_gaussian(mean: float, sd: float) -> float:
    return mean + py5.random_gaussian() * sd


def create_smoke_texture() -> py5.Py5Graphics:
    img = py5.create_graphics(64, 64)
    img.begin_draw()
    img.clear()
    img.no_stroke()
    for radius in range(64, 0, -2):
        alpha = py5.remap(radius, 64, 0, 0, 22)
        img.fill(255, alpha)
        img.circle(32, 32, radius)
    img.end_draw()
    return img


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(
            random_gaussian(0, 0.3),
            random_gaussian(-1, 0.3),
        )
        self.acceleration = py5.Py5Vector(0, 0)
        self.lifespan = 100.0

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
        py5.tint(255, self.lifespan)
        py5.image_mode(py5.CENTER)
        py5.image(texture, self.position.x, self.position.y)
        py5.no_tint()

    def is_dead(self) -> bool:
        return self.lifespan < 0.0


class Emitter:
    def __init__(self, x: float, y: float) -> None:
        self.origin = py5.Py5Vector(x, y)
        self.particles: list[Particle] = []

    def run(self) -> None:
        for particle in self.particles:
            particle.run()
        self.particles = [particle for particle in self.particles if not particle.is_dead()]

    def apply_force(self, force: py5.Py5Vector) -> None:
        for particle in self.particles:
            particle.apply_force(force)

    def add_particle(self) -> None:
        self.particles.append(Particle(self.origin.x, self.origin.y))


def setup() -> None:
    global emitter, texture
    py5.size(640, 240)
    texture = create_smoke_texture()
    emitter = Emitter(py5.width / 2, py5.height - 75)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_vector(v: py5.Py5Vector, pos: py5.Py5Vector, scale: float) -> None:
    arrowsize = 4
    with py5.push_matrix():
        py5.translate(pos.x, pos.y)
        py5.stroke(255)
        py5.rotate(v.heading)
        length = v.mag * scale
        py5.line(0, 0, length, 0)
        py5.line(length, 0, length - arrowsize, arrowsize / 2)
        py5.line(length, 0, length - arrowsize, -arrowsize / 2)


def draw() -> None:
    py5.background(0)

    dx = py5.remap(py5.mouse_x, 0, py5.width, -0.2, 0.2)
    wind = py5.Py5Vector(dx, 0)
    emitter.apply_force(wind)
    emitter.run()
    emitter.add_particle()

    draw_vector(wind, py5.Py5Vector(py5.width / 2, 50), 500)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "image_texture_system_smoke_####.png"))


py5.run_sketch()
