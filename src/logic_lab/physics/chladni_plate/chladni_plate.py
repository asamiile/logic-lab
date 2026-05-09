from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PARTICLE_COUNT = 900
mode_a = 3
mode_b = 5
particles: list[Particle] = []


@dataclass
class Particle:
    x: float
    y: float

    def update(self) -> None:
        nx = self.x / py5.width
        ny = self.y / py5.height
        eps = 0.004
        here = abs(field(nx, ny))
        grad_x = abs(field(nx + eps, ny)) - here
        grad_y = abs(field(nx, ny + eps)) - here
        self.x -= grad_x * 580 + py5.random(-0.35, 0.35)
        self.y -= grad_y * 580 + py5.random(-0.35, 0.35)
        self.x = py5.constrain(self.x, 6, py5.width - 6)
        self.y = py5.constrain(self.y, 6, py5.height - 6)


def field(x: float, y: float) -> float:
    return math.sin(mode_a * math.pi * x) * math.sin(mode_b * math.pi * y) - math.sin(
        mode_b * math.pi * x
    ) * math.sin(mode_a * math.pi * y)


def setup() -> None:
    py5.size(640, 640)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_particles()


def reset_particles() -> None:
    global particles
    particles = [
        Particle(py5.random(py5.width), py5.random(py5.height)) for _ in range(PARTICLE_COUNT)
    ]


def draw_background() -> None:
    step = 7
    py5.no_stroke()
    for y in range(0, py5.height, step):
        for x in range(0, py5.width, step):
            value = abs(field((x + step * 0.5) / py5.width, (y + step * 0.5) / py5.height))
            brightness = 12 + py5.constrain(value * 48, 0, 42)
            py5.fill(224, 30, brightness, 88)
            py5.rect(x, y, step + 1, step + 1)


def draw() -> None:
    draw_background()
    py5.no_stroke()
    for particle in particles:
        particle.update()
        value = abs(field(particle.x / py5.width, particle.y / py5.height))
        py5.fill(42, 54, 95, 28 + (1 - min(1, value)) * 60)
        py5.circle(particle.x, particle.y, 2.2)

    py5.fill(42, 70, 96)
    py5.text_size(16)
    py5.text(f"modes {mode_a}:{mode_b}", 22, 28)


def key_pressed() -> None:
    global mode_a, mode_b
    if py5.key == "r":
        reset_particles()
    elif py5.key == "a":
        mode_a = 2 + mode_a % 8
        reset_particles()
    elif py5.key == "b":
        mode_b = 2 + mode_b % 8
        reset_particles()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "chladni_plate_####.png"))


py5.run_sketch()
