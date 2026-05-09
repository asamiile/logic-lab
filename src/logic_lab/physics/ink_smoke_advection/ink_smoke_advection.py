from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(91)
particles: list[InkParticle] = []
palette_index = 0
phase = 0.0
auto_emit = True
show_flow = False

PALETTES = [
    [(214, 72, 48), (188, 56, 60), (268, 44, 54), (38, 62, 72)],
    [(354, 58, 70), (28, 66, 82), (48, 42, 88), (318, 38, 64)],
    [(178, 58, 52), (206, 72, 58), (236, 46, 48), (124, 38, 50)],
]


@dataclass
class InkParticle:
    x: float
    y: float
    vx: float
    vy: float
    age: int
    lifespan: int
    radius: float
    hue: float
    saturation: float
    brightness: float

    def update(self) -> None:
        curl = curl_noise(self.x, self.y, phase)
        lift = py5.Py5Vector(0.018, -0.012)
        self.vx = self.vx * 0.965 + curl.x * 0.42 + lift.x
        self.vy = self.vy * 0.965 + curl.y * 0.42 + lift.y
        self.x += self.vx
        self.y += self.vy
        self.radius += 0.024
        self.age += 1

    @property
    def life(self) -> float:
        return max(0.0, 1.0 - self.age / self.lifespan)

    def is_dead(self) -> bool:
        margin = 80
        return (
            self.age >= self.lifespan
            or self.x < -margin
            or self.x > py5.width + margin
            or self.y < -margin
            or self.y > py5.height + margin
        )


def setup() -> None:
    py5.size(900, 680)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.noise_seed(91)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()


def reset_scene() -> None:
    global particles, phase
    particles = []
    phase = 0.0
    py5.background(38, 9, 97)
    for i in range(4):
        emit_burst(py5.width * (0.24 + i * 0.17), py5.height * (0.58 + math.sin(i) * 0.08), 80)


def draw() -> None:
    global phase
    phase += 0.012
    fade_paper()
    if auto_emit:
        emit_burst(py5.width * 0.38 + math.sin(phase * 1.7) * 170, py5.height * 0.62, 5)
    if py5.is_mouse_pressed:
        emit_burst(float(py5.mouse_x), float(py5.mouse_y), 18)
    update_particles()
    if show_flow:
        draw_flow_vectors()


def fade_paper() -> None:
    py5.no_stroke()
    py5.fill(38, 9, 97, 4)
    py5.rect(0, 0, py5.width, py5.height)
    for _ in range(42):
        x = rng.uniform(0, py5.width)
        y = rng.uniform(0, py5.height)
        py5.fill(38, 4, rng.uniform(88, 100), 2.6)
        py5.circle(x, y, rng.uniform(1.2, 3.8))


def emit_burst(x: float, y: float, amount: int) -> None:
    palette = PALETTES[palette_index]
    for _ in range(amount):
        angle = rng.uniform(-math.pi, math.pi)
        speed = abs(rng.gauss(0.9, 0.42))
        hue, saturation, brightness = rng.choice(palette)
        particles.append(
            InkParticle(
                x=x + rng.gauss(0, 14),
                y=y + rng.gauss(0, 12),
                vx=math.cos(angle) * speed + rng.gauss(0, 0.18),
                vy=math.sin(angle) * speed * 0.7 + rng.gauss(-0.18, 0.14),
                age=0,
                lifespan=rng.randrange(170, 420),
                radius=rng.uniform(4.5, 12.0),
                hue=hue + rng.gauss(0, 5),
                saturation=saturation,
                brightness=brightness,
            )
        )
    del particles[:-2600]


def curl_noise(x: float, y: float, t: float) -> py5.Py5Vector:
    scale = 0.006
    eps = 0.015
    nx = x * scale
    ny = y * scale
    n1 = py5.noise(nx, ny + eps, t)
    n2 = py5.noise(nx, ny - eps, t)
    n3 = py5.noise(nx + eps, ny, t)
    n4 = py5.noise(nx - eps, ny, t)
    dx = (n1 - n2) / (2 * eps)
    dy = (n3 - n4) / (2 * eps)
    vector = py5.Py5Vector(dx, -dy)
    if vector.mag > 0:
        vector.normalize()
    strength = 0.35 + py5.noise(nx * 0.42 + 100, ny * 0.42, t * 0.7) * 1.1
    return vector * strength


def update_particles() -> None:
    py5.no_stroke()
    next_particles = []
    for particle in particles:
        particle.update()
        if particle.is_dead():
            continue
        draw_particle(particle)
        next_particles.append(particle)
    particles[:] = next_particles


def draw_particle(particle: InkParticle) -> None:
    life = particle.life
    bloom = particle.radius * (1.0 + (1.0 - life) * 2.1)
    edge_alpha = 5.5 * life
    core_alpha = 9.0 * life
    py5.fill(particle.hue, particle.saturation * 0.58, particle.brightness + 20, edge_alpha)
    py5.circle(particle.x, particle.y, bloom * 3.4)
    py5.fill(particle.hue, particle.saturation, particle.brightness, core_alpha)
    py5.circle(particle.x, particle.y, bloom)
    if particle.age % 5 == 0:
        py5.fill(
            particle.hue, particle.saturation * 0.7, min(100, particle.brightness + 12), 3.0 * life
        )
        py5.circle(
            particle.x + rng.gauss(0, bloom * 0.35),
            particle.y + rng.gauss(0, bloom * 0.35),
            bloom * 0.55,
        )


def draw_flow_vectors() -> None:
    py5.stroke(210, 28, 40, 18)
    py5.stroke_weight(1)
    for y in range(60, py5.height, 60):
        for x in range(60, py5.width, 60):
            v = curl_noise(x, y, phase) * 18
            py5.line(x, y, x + v.x, y + v.y)


def key_pressed() -> None:
    global auto_emit, palette_index, show_flow
    if py5.key == "r":
        reset_scene()
    elif py5.key == " ":
        auto_emit = not auto_emit
    elif py5.key == "p":
        palette_index = (palette_index + 1) % len(PALETTES)
        reset_scene()
    elif py5.key == "v":
        show_flow = not show_flow
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ink_smoke_advection_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
