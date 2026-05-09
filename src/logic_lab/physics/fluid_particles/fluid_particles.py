from pathlib import Path
from random import Random

import py5
from logic_lab.shared.physics2d import (
    Particle,
    Vec2,
    apply_density_pressure,
    drag_force,
    gravity_force,
    spawn_particles,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(9)
particles: list[Particle] = []


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    particles.extend(spawn_particles(180, Vec2(320, 90), rng, (10, 80), (3, 5)))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(244)
    dt = 1 / 60

    if py5.is_mouse_pressed:
        particles.extend(spawn_particles(4, Vec2(py5.mouse_x, py5.mouse_y), rng, (10, 95), (3, 5)))
        del particles[: max(0, len(particles) - 260)]

    apply_density_pressure(particles, interaction_radius=26, pressure=520, viscosity=0.18)
    for particle in particles:
        particle.apply_force(gravity_force(260 * particle.mass))
        particle.apply_force(drag_force(particle, 0.002))
        particle.step(dt)
        bounce_particle(particle)

    py5.no_stroke()
    for particle in particles:
        py5.fill(38, 130, 210, 150)
        py5.circle(particle.pos.x, particle.pos.y, particle.radius * 2.4)


def bounce_particle(particle: Particle) -> None:
    if particle.pos.x < particle.radius:
        particle.pos.x = particle.radius
        particle.vel.x *= -0.55
    elif particle.pos.x > py5.width - particle.radius:
        particle.pos.x = py5.width - particle.radius
        particle.vel.x *= -0.55
    if particle.pos.y < particle.radius:
        particle.pos.y = particle.radius
        particle.vel.y *= -0.45
    elif particle.pos.y > py5.height - particle.radius:
        particle.pos.y = py5.height - particle.radius
        particle.vel.y *= -0.45
        particle.vel.x *= 0.96


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fluid_particles_####.png"))


py5.run_sketch()
