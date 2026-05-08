from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(73)


@dataclass
class LightParticle:
    x: float
    y: float
    vx: float
    vy: float
    hue: float


particles: list[LightParticle] = []
light_sources: list[tuple[float, float, float]] = []


def setup() -> None:
    py5.size(900, 640)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_field()


def reset_field() -> None:
    global particles, light_sources
    particles = [
        LightParticle(
            rng.uniform(0, py5.width),
            rng.uniform(0, py5.height),
            rng.uniform(-0.25, 0.25),
            rng.uniform(-0.18, 0.18),
            rng.choice([44, 188, 282]),
        )
        for _ in range(900)
    ]
    light_sources = [
        (py5.width * 0.25, py5.height * 0.36, 46),
        (py5.width * 0.68, py5.height * 0.48, 198),
        (py5.width * 0.48, py5.height * 0.74, 310),
    ]


def draw() -> None:
    py5.no_stroke()
    py5.fill(230, 34, 6, 18)
    py5.rect(0, 0, py5.width, py5.height)
    update_particles()
    draw_sources()


def update_particles() -> None:
    py5.no_stroke()
    mouse_source = (float(py5.mouse_x), float(py5.mouse_y), 56) if py5.is_mouse_pressed else None
    sources = light_sources + ([mouse_source] if mouse_source else [])
    for particle in particles:
        particle.x = (particle.x + particle.vx) % py5.width
        particle.y = (particle.y + particle.vy) % py5.height
        intensity, hue = illumination(particle.x, particle.y, sources)
        size = 1.2 + intensity * 4.2
        py5.fill(hue, 54 + intensity * 36, 16 + intensity * 84, 18 + intensity * 70)
        py5.circle(particle.x, particle.y, size)


def illumination(
    x: float, y: float, sources: list[tuple[float, float, float]]
) -> tuple[float, float]:
    total = 0.0
    hue_x = 0.0
    hue_y = 0.0
    for sx, sy, hue in sources:
        distance_sq = max(900.0, (x - sx) ** 2 + (y - sy) ** 2)
        value = 7200.0 / distance_sq
        total += value
        angle = math.radians(hue)
        hue_x += math.cos(angle) * value
        hue_y += math.sin(angle) * value
    mixed_hue = math.degrees(math.atan2(hue_y, hue_x)) % 360
    return min(1.0, total), mixed_hue


def draw_sources() -> None:
    for sx, sy, hue in light_sources:
        py5.no_stroke()
        for radius, alpha in ((110, 5), (54, 16), (18, 88)):
            py5.fill(hue, 82, 100, alpha)
            py5.circle(sx, sy, radius)


def key_pressed() -> None:
    if py5.key == "r":
        reset_field()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "light_falloff_field_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
