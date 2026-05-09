from pathlib import Path
from random import Random

import py5
from logic_lab.shared.physics2d import (
    Particle,
    Vec2,
    drag_force,
    radial_force,
    spawn_particles,
    vortex_force,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(42)
particles: list[Particle] = []


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    particles.extend(spawn_particles(220, Vec2(320, 180), rng, lifespan=None))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(8, 12, 16, 32)
    center = Vec2(py5.mouse_x, py5.mouse_y) if py5.is_mouse_pressed else Vec2(320, 180)
    dt = 1 / 60

    for particle in particles:
        particle.apply_force(radial_force(particle.pos, center, 70000))
        particle.apply_force(vortex_force(particle.pos, center, 4300))
        particle.apply_force(drag_force(particle, 0.003))
        particle.step(dt)
        if not (0 <= particle.pos.x <= py5.width and 0 <= particle.pos.y <= py5.height):
            particle.pos = Vec2(320, 180)
            particle.vel = Vec2.from_angle(rng.random() * py5.TWO_PI, rng.uniform(70, 170))

    py5.no_stroke()
    for particle in particles:
        speed = min(255, particle.vel.mag() * 1.2)
        py5.fill(245, 180, 70, 90 + speed * 0.4)
        py5.circle(particle.pos.x, particle.pos.y, particle.radius * 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "particle_force_fields_####.png"))


py5.run_sketch()
