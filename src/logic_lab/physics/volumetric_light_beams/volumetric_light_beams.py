from __future__ import annotations

import math
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(42)
particles: list[tuple[float, float, float]] = []
phase = 0.0


def setup() -> None:
    py5.size(900, 640)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_particles()


def reset_particles() -> None:
    global particles
    particles = [
        (rng.uniform(0, py5.width), rng.uniform(0, py5.height), rng.uniform(0.7, 2.4))
        for _ in range(620)
    ]


def draw() -> None:
    global phase
    phase += 0.012
    py5.background(220, 36, 9)
    beams = beam_definitions()
    draw_beams(beams)
    draw_fog_particles(beams)


def beam_definitions() -> list[tuple[py5.Py5Vector, float, float, float]]:
    origin = py5.Py5Vector(py5.width * 0.5, -30)
    base = py5.HALF_PI
    return [
        (origin + py5.Py5Vector(-140, 0), base - 0.38 + math.sin(phase) * 0.05, 0.25, 48),
        (origin + py5.Py5Vector(60, 0), base + 0.02 + math.sin(phase * 0.8) * 0.04, 0.18, 198),
        (origin + py5.Py5Vector(210, 0), base + 0.32 + math.sin(phase * 1.2) * 0.05, 0.22, 292),
    ]


def draw_beams(beams: list[tuple[py5.Py5Vector, float, float, float]]) -> None:
    py5.no_stroke()
    for origin, angle, spread, hue in beams:
        for alpha, length, width_scale in ((8, 980, 1.0), (15, 760, 0.62), (24, 520, 0.34)):
            left = (
                origin
                + py5.Py5Vector(
                    math.cos(angle - spread * width_scale),
                    math.sin(angle - spread * width_scale),
                )
                * length
            )
            right = (
                origin
                + py5.Py5Vector(
                    math.cos(angle + spread * width_scale),
                    math.sin(angle + spread * width_scale),
                )
                * length
            )
            py5.fill(hue, 48, 100, alpha)
            py5.begin_shape()
            py5.vertex(origin.x, origin.y)
            py5.vertex(left.x, left.y)
            py5.vertex(right.x, right.y)
            py5.end_shape(py5.CLOSE)
        py5.fill(hue, 70, 100, 42)
        py5.circle(origin.x, origin.y + 30, 26)


def draw_fog_particles(beams: list[tuple[py5.Py5Vector, float, float, float]]) -> None:
    py5.no_stroke()
    for x, y, radius in particles:
        drift_x = x + math.sin(y * 0.014 + phase * 2.1) * 18
        brightness, hue = particle_light(drift_x, y, beams)
        if brightness <= 0:
            py5.fill(210, 12, 88, 5)
        else:
            py5.fill(hue, 34, 96, 10 + brightness * 58)
        py5.circle(drift_x % py5.width, y, radius + brightness * 2.4)


def particle_light(
    x: float, y: float, beams: list[tuple[py5.Py5Vector, float, float, float]]
) -> tuple[float, float]:
    best = 0.0
    best_hue = 48.0
    point = py5.Py5Vector(x, y)
    for origin, angle, spread, hue in beams:
        to_point = point - origin
        distance = max(1.0, to_point.mag)
        theta = math.atan2(to_point.y, to_point.x)
        delta = abs(math.atan2(math.sin(theta - angle), math.cos(theta - angle)))
        if delta < spread:
            intensity = (
                (1 - delta / spread) ** 2 * min(1.0, distance / 260) / (1 + distance * 0.0012)
            )
            if intensity > best:
                best = intensity
                best_hue = hue
    return min(1.0, best), best_hue


def key_pressed() -> None:
    if py5.key == "r":
        reset_particles()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "volumetric_light_beams_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
