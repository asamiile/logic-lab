from pathlib import Path
from random import choice

import py5

BASE_DIR = Path(__file__).parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"

particle_system: "ParticleSystem"
textures: list[py5.Py5Graphics] = []


def create_glow_texture(
    base_color: tuple[int, int, int],
    highlight_color: tuple[int, int, int],
) -> py5.Py5Graphics:
    img = py5.create_graphics(64, 64)
    img.begin_draw()
    img.clear()
    img.no_stroke()
    for radius in range(64, 0, -2):
        t = radius / 64
        alpha = int((1 - t) * 55)
        r = int(base_color[0] * t + highlight_color[0] * (1 - t))
        g = int(base_color[1] * t + highlight_color[1] * (1 - t))
        b = int(base_color[2] * t + highlight_color[2] * (1 - t))
        img.fill(r, g, b, alpha)
        img.circle(32, 32, radius)
    img.fill(*highlight_color, 180)
    img.circle(32, 32, 10)
    img.end_draw()
    return img


class Particle:
    def __init__(self, x: float, y: float, img: py5.Py5Graphics) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        angle = py5.random(py5.TWO_PI)
        self.velocity = py5.Py5Vector(py5.cos(angle), py5.sin(angle))
        self.position = py5.Py5Vector(x, y)
        self.lifespan = 255.0
        self.img = img

    def run(self) -> None:
        self.update()
        self.show()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.lifespan -= 5.0

    def show(self) -> None:
        py5.image_mode(py5.CENTER)
        py5.tint(self.lifespan)
        py5.image(self.img, self.position.x, self.position.y, 32, 32)
        py5.no_tint()

    def is_dead(self) -> bool:
        return self.lifespan <= 0.0


class ParticleSystem:
    def __init__(self, imgs: list[py5.Py5Graphics]) -> None:
        self.particles: list[Particle] = []
        self.textures = imgs

    def add_particle(self, x: float, y: float) -> None:
        img = choice(self.textures)
        self.particles.append(Particle(x, y, img))

    def apply_force(self, force: py5.Py5Vector) -> None:
        for particle in self.particles:
            particle.apply_force(force)

    def update(self) -> None:
        for particle in self.particles:
            particle.run()
        self.particles = [particle for particle in self.particles if not particle.is_dead()]


def setup() -> None:
    global particle_system, textures
    py5.size(640, 240)
    textures = [
        create_glow_texture((255, 80, 20), (255, 240, 120)),
        create_glow_texture((60, 150, 255), (220, 245, 255)),
        create_glow_texture((180, 120, 255), (255, 255, 255)),
    ]
    particle_system = ParticleSystem(textures)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.blend_mode(py5.ADD)
    py5.clear()
    py5.background(0)

    particle_system.add_particle(py5.mouse_x, py5.mouse_y)
    up = py5.Py5Vector(0, -0.2)
    particle_system.apply_force(up)
    particle_system.update()

    py5.blend_mode(py5.BLEND)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_textures_array_####.png"))


py5.run_sketch()
