from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Preset:
    name: str
    seed: int
    emitters: int
    gravity: float
    wind: float
    swirl: float
    hue: float


@dataclass
class Pollen:
    position: py5.Py5Vector
    velocity: py5.Py5Vector
    age: int
    lifespan: int
    radius: float


PRESETS = [
    Preset("pollen cloud", 21, 5, 0.006, 0.045, 0.24, 48),
    Preset("dandelion drift", 37, 3, 0.002, 0.072, 0.34, 58),
    Preset("seed burst", 52, 1, 0.014, 0.028, 0.18, 34),
]


class PollenField:
    def __init__(self, width: int, height: int, preset: Preset) -> None:
        self.width = width
        self.height = height
        self.preset = preset
        self.rng = Random(preset.seed)
        py5.noise_seed(preset.seed)
        self.particles: list[Pollen] = []
        self.emitters = self._make_emitters()

    def _make_emitters(self) -> list[py5.Py5Vector]:
        emitters = []
        for i in range(self.preset.emitters):
            x = self.width * (0.22 + 0.56 * (i + 0.5) / self.preset.emitters)
            y = self.height * self.rng.uniform(0.58, 0.82)
            emitters.append(py5.Py5Vector(x, y))
        return emitters

    def emit(self) -> None:
        amount = 16 if self.preset.name == "seed burst" and len(self.particles) < 420 else 5
        for emitter in self.emitters:
            for _ in range(amount):
                angle = self.rng.uniform(-py5.PI * 0.92, -py5.PI * 0.08)
                if self.preset.name == "seed burst":
                    angle = self.rng.uniform(-py5.PI, 0)
                speed = self.rng.uniform(0.45, 2.2)
                position = py5.Py5Vector(
                    emitter.x + self.rng.uniform(-8, 8),
                    emitter.y + self.rng.uniform(-8, 8),
                )
                velocity = py5.Py5Vector(py5.cos(angle), py5.sin(angle)) * speed
                self.particles.append(
                    Pollen(
                        position=position,
                        velocity=velocity,
                        age=0,
                        lifespan=self.rng.randrange(180, 520),
                        radius=self.rng.uniform(1.6, 4.8),
                    )
                )
        self.particles = self.particles[-1800:]

    def update_and_draw(self) -> None:
        self.emit()
        py5.no_stroke()
        next_particles = []
        for particle in self.particles:
            wind_noise = py5.noise(
                particle.position.x * 0.006, particle.position.y * 0.006, particle.age * 0.01
            )
            angle = (wind_noise - 0.5) * py5.TWO_PI * self.preset.swirl
            wind = py5.Py5Vector(self.preset.wind + py5.cos(angle) * 0.028, py5.sin(angle) * 0.035)
            particle.velocity += wind
            particle.velocity.y += self.preset.gravity
            particle.velocity *= 0.985
            particle.position += particle.velocity
            particle.age += 1

            if (
                particle.age >= particle.lifespan
                or particle.position.x > self.width + 30
                or particle.position.y > self.height + 30
            ):
                continue

            life = 1.0 - particle.age / particle.lifespan
            hue = self.preset.hue + py5.sin(particle.age * 0.05) * 14
            py5.fill(hue, 44, 94, 52 * life)
            py5.circle(particle.position.x, particle.position.y, particle.radius * (0.6 + life))
            if self.preset.name == "dandelion drift":
                py5.stroke(hue, 20, 96, 20 * life)
                py5.stroke_weight(0.6)
                py5.line(
                    particle.position.x,
                    particle.position.y,
                    particle.position.x - particle.velocity.x * 5,
                    particle.position.y - particle.velocity.y * 5,
                )
                py5.no_stroke()
            next_particles.append(particle)
        self.particles = next_particles

    def draw_emitters(self) -> None:
        py5.no_stroke()
        for emitter in self.emitters:
            py5.fill(112, 48, 40, 82)
            py5.rect(emitter.x - 3, emitter.y, 6, self.height - emitter.y)
            py5.fill(54, 68, 88, 80)
            py5.circle(emitter.x, emitter.y, 18)


field: PollenField
preset_index = 0


def reset(index: int) -> None:
    global field, preset_index
    preset_index = index % len(PRESETS)
    field = PollenField(py5.width, py5.height, PRESETS[preset_index])
    py5.background(205, 16, 96)


def setup() -> None:
    py5.size(900, 720)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset(0)


def draw() -> None:
    py5.no_stroke()
    py5.fill(205, 16, 96, 8)
    py5.rect(0, 0, py5.width, py5.height)
    field.draw_emitters()
    field.update_and_draw()


def key_pressed() -> None:
    if py5.key in {"1", "2", "3"}:
        reset(int(py5.key) - 1)
    elif py5.key == "r":
        reset(preset_index)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pollen_dispersal_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
