import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
particles: list[dict] = []


def setup() -> None:
    py5.size(1000, 600)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.text_size(80)
    py5.text_align(py5.CENTER, py5.CENTER)
    initialize_particles()


def initialize_particles() -> None:
    global particles
    particles = []
    text = "ART"
    py5.text_font(py5.create_font("Arial", 80))

    for i, char in enumerate(text):
        x_base = py5.width / 2 - 100 + i * 80
        for _ in range(15):
            particles.append(
                {
                    "x": x_base + random.uniform(-30, 30),
                    "y": py5.height / 2 + random.uniform(-40, 40),
                    "vx": random.uniform(-2, 2),
                    "vy": random.uniform(-3, 1),
                    "life": random.uniform(200, 400),
                }
            )


def draw() -> None:
    py5.background(20)

    for particle in particles[:]:
        particle["vy"] += 0.1
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        alpha = int(255 * (particle["life"] / 400))
        py5.fill(200, 150, 255, alpha)
        py5.stroke_weight(0)
        py5.circle(particle["x"], particle["y"], 3)

        if particle["life"] <= 0:
            particles.remove(particle)

    if len(particles) < 100:
        initialize_particles()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "typography_particles_####.png"))


py5.run_sketch()
