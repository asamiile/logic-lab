from dataclasses import dataclass
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass
class Particle:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    attached: bool = False

    def update(self):
        if not self.attached:
            if self.vx == 0 and self.vy == 0:
                angle = np.random.uniform(0, 2 * np.pi)
                self.vx = np.cos(angle) * 2
                self.vy = np.sin(angle) * 2
            else:
                angle = np.arctan2(self.vy, self.vx) + np.random.normal(0, 0.3)
                self.vx = np.cos(angle) * 2
                self.vy = np.sin(angle) * 2

            self.x += self.vx
            self.y += self.vy

    def is_outside(self, width, height, margin=50):
        return (
            self.x < -margin
            or self.x > width + margin
            or self.y < -margin
            or self.y > height + margin
        )


class DLASimulation:
    def __init__(self, width=800, height=800, attraction_distance=25):
        self.width = width
        self.height = height
        self.attraction_distance = attraction_distance
        self.particles = []
        self.attached = []

        self.seed_particle = Particle(width / 2, height / 2)
        self.seed_particle.attached = True
        self.attached.append(self.seed_particle)

    def add_random_particle(self):
        angle = np.random.uniform(0, 2 * np.pi)
        distance = 300
        x = self.width / 2 + np.cos(angle) * distance
        y = self.height / 2 + np.sin(angle) * distance
        particle = Particle(x, y)
        self.particles.append(particle)

    def distance(self, p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return np.sqrt(dx * dx + dy * dy)

    def check_attachment(self):
        to_remove = []
        for i, particle in enumerate(self.particles):
            for attached_p in self.attached:
                if self.distance(particle, attached_p) < self.attraction_distance:
                    particle.attached = True
                    self.attached.append(particle)
                    to_remove.append(i)
                    break

        for i in sorted(to_remove, reverse=True):
            self.particles.pop(i)

    def update(self):
        for particle in self.particles:
            particle.update()

        to_remove = []
        for i, particle in enumerate(self.particles):
            if particle.is_outside(self.width, self.height):
                to_remove.append(i)

        for i in sorted(to_remove, reverse=True):
            self.particles.pop(i)

        self.check_attachment()

    def draw_particles(self):
        py5.no_stroke()
        py5.fill(50)
        for particle in self.attached:
            py5.circle(particle.x, particle.y, 2)


def setup():
    py5.size(800, 800)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global dla
    dla = DLASimulation(py5.width, py5.height, attraction_distance=25)


def draw():
    py5.background(255)

    for _ in range(5):
        if len(dla.particles) < 3000:
            dla.add_random_particle()

        dla.update()

    dla.draw_particles()

    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text(f"Particles: {len(dla.particles)} | Attached: {len(dla.attached)}", 10, 20)


def key_pressed():
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "dla_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
