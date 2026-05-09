from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from random import Random

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_STEP = 5
rng = Random(208)
particles: list[DyeParticle] = []
density: np.ndarray
phase = 0.0
palette_index = 0
auto_emit = True

PALETTES = [
    [(202, 82, 82), (176, 62, 72), (258, 54, 76)],
    [(328, 72, 80), (18, 74, 88), (46, 66, 92)],
    [(150, 64, 70), (188, 76, 82), (220, 58, 84)],
]


@dataclass
class DyeParticle:
    x: float
    y: float
    vx: float
    vy: float
    age: int
    lifespan: int
    hue: float
    saturation: float
    brightness: float

    def update(self) -> None:
        flow = plume_flow(self.x, self.y, phase)
        buoyancy = py5.Py5Vector(0.0, -0.022)
        self.vx = self.vx * 0.972 + flow.x * 0.34 + buoyancy.x
        self.vy = self.vy * 0.972 + flow.y * 0.34 + buoyancy.y
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    @property
    def life(self) -> float:
        return max(0.0, 1.0 - self.age / self.lifespan)

    def is_dead(self) -> bool:
        return self.age >= self.lifespan or self.y < -70 or self.x < -70 or self.x > py5.width + 70


def setup() -> None:
    py5.size(900, 680)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.noise_seed(208)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()


def reset_scene() -> None:
    global particles, density, phase
    rows = py5.height // GRID_STEP
    cols = py5.width // GRID_STEP
    density = np.zeros((rows, cols), dtype=np.float32)
    particles = []
    phase = 0.0
    for i in range(3):
        emit_plume(py5.width * (0.32 + i * 0.16), py5.height * 0.82, 120, i)


def draw() -> None:
    global phase
    phase += 0.014
    if auto_emit:
        emit_plume(
            py5.width * 0.5 + math.sin(phase * 1.4) * 180, py5.height * 0.86, 8, int(phase * 5) % 3
        )
    if py5.is_mouse_pressed:
        emit_plume(float(py5.mouse_x), float(py5.mouse_y), 28, int(phase * 7) % 3)
    update_density()
    update_particles()
    draw_density()
    draw_particles()


def emit_plume(x: float, y: float, amount: int, color_index: int) -> None:
    hue, saturation, brightness = PALETTES[palette_index][color_index % 3]
    for _ in range(amount):
        angle = rng.uniform(-math.pi * 0.82, -math.pi * 0.18)
        speed = abs(rng.gauss(1.05, 0.38))
        particles.append(
            DyeParticle(
                x=x + rng.gauss(0, 12),
                y=y + rng.gauss(0, 8),
                vx=math.cos(angle) * speed * 0.34 + rng.gauss(0, 0.16),
                vy=math.sin(angle) * speed + rng.gauss(0, 0.12),
                age=0,
                lifespan=rng.randrange(210, 520),
                hue=hue + rng.gauss(0, 4),
                saturation=saturation,
                brightness=brightness,
            )
        )
    del particles[:-3200]


def plume_flow(x: float, y: float, t: float) -> py5.Py5Vector:
    nx = x * 0.005
    ny = y * 0.005
    angle = py5.noise(nx, ny, t) * py5.TWO_PI * 2.0
    swirl = py5.noise(nx + 100, ny - 40, t * 0.8)
    return py5.Py5Vector(math.cos(angle), math.sin(angle)) * (0.45 + swirl * 0.9)


def update_density() -> None:
    global density
    density *= 0.965
    density = (
        density * 4
        + np.roll(density, 1, axis=0)
        + np.roll(density, -1, axis=0)
        + np.roll(density, 1, axis=1)
        + np.roll(density, -1, axis=1)
    ) / 8.0


def update_particles() -> None:
    next_particles = []
    rows, cols = density.shape
    for particle in particles:
        particle.update()
        if particle.is_dead():
            continue
        col = int(particle.x / GRID_STEP)
        row = int(particle.y / GRID_STEP)
        if 0 <= row < rows and 0 <= col < cols:
            density[row, col] = min(1.0, density[row, col] + particle.life * 0.08)
        next_particles.append(particle)
    particles[:] = next_particles


def draw_density() -> None:
    py5.background(218, 24, 10)
    rows, cols = density.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            value = float(density[row, col])
            if value <= 0.004:
                continue
            hue = 204 + value * 36
            py5.fill(hue, 52, 28 + value * 64, min(56, value * 80))
            py5.rect(col * GRID_STEP, row * GRID_STEP, GRID_STEP + 1, GRID_STEP + 1)


def draw_particles() -> None:
    py5.no_stroke()
    for particle in particles:
        life = particle.life
        size = 2.4 + (1 - life) * 8.0
        py5.fill(particle.hue, particle.saturation * 0.78, particle.brightness, 8 + life * 28)
        py5.circle(particle.x, particle.y, size * 2.6)
        py5.fill(particle.hue, particle.saturation, particle.brightness + 8, 18 + life * 38)
        py5.circle(particle.x, particle.y, size)


def key_pressed() -> None:
    global auto_emit, palette_index
    if py5.key == "r":
        reset_scene()
    elif py5.key == " ":
        auto_emit = not auto_emit
    elif py5.key == "p":
        palette_index = (palette_index + 1) % len(PALETTES)
        reset_scene()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "dye_plume_field_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
