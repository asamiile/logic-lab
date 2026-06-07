"""
Predator-Prey Flocking.

Extends Reynolds' classic Boids flocking (separation, alignment, cohesion)
with predator agents that hunt the flock. Prey birds exhibit emergent
escape maneuvers, splitting and reforming under threat.

Prey rules:
    - Separation: avoid crowding neighbors
    - Alignment: steer toward average heading of neighbors
    - Cohesion: steer toward average position of neighbors
    - Fear: flee from nearby predators (overrides all other forces)

Predator rules:
    - Chase the nearest prey or the center of the nearest cluster
    - Maintain some spacing from other predators
"""

import math
import random
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 900
HEIGHT = 900
NUM_PREY = 200
NUM_PREDATORS = 3

# Prey parameters
PREY_SPEED = 2.8
PREY_MAX_FORCE = 0.15
PREY_VISION = 60.0
PREY_SEP_DIST = 20.0
PREY_FEAR_DIST = 120.0
PREY_FEAR_WEIGHT = 3.5

# Predator parameters
PRED_SPEED = 3.6
PRED_MAX_FORCE = 0.12
PRED_VISION = 180.0


@dataclass
class Agent:
    x: float
    y: float
    vx: float
    vy: float
    is_predator: bool = False

    @property
    def speed(self) -> float:
        return PRED_SPEED if self.is_predator else PREY_SPEED

    def heading(self) -> float:
        return math.atan2(self.vy, self.vx)


agents: list[Agent]


def _initialize() -> None:
    global agents
    rng = random.Random(99)
    agents = []
    for _ in range(NUM_PREY):
        angle = rng.uniform(0, math.tau)
        spd = rng.uniform(PREY_SPEED * 0.5, PREY_SPEED)
        agents.append(
            Agent(
                x=rng.uniform(0, WIDTH),
                y=rng.uniform(0, HEIGHT),
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd,
            )
        )
    for _ in range(NUM_PREDATORS):
        angle = rng.uniform(0, math.tau)
        agents.append(
            Agent(
                x=rng.uniform(0, WIDTH),
                y=rng.uniform(0, HEIGHT),
                vx=math.cos(angle) * PRED_SPEED,
                vy=math.sin(angle) * PRED_SPEED,
                is_predator=True,
            )
        )


def _clamp_speed(vx: float, vy: float, max_spd: float) -> tuple[float, float]:
    spd = math.hypot(vx, vy)
    if spd > max_spd:
        vx = vx / spd * max_spd
        vy = vy / spd * max_spd
    elif spd < max_spd * 0.3:
        if spd > 1e-6:
            vx = vx / spd * max_spd * 0.3
            vy = vy / spd * max_spd * 0.3
    return vx, vy


def _steer(
    ax: float,
    ay: float,
    avx: float,
    avy: float,
    tx: float,
    ty: float,
    max_speed: float,
    max_force: float,
) -> tuple[float, float]:
    """Return steering force toward target."""
    dx = tx - ax
    dy = ty - ay
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return 0.0, 0.0
    desired_vx = dx / dist * max_speed
    desired_vy = dy / dist * max_speed
    fx = desired_vx - avx
    fy = desired_vy - avy
    mag = math.hypot(fx, fy)
    if mag > max_force:
        fx = fx / mag * max_force
        fy = fy / mag * max_force
    return fx, fy


def _update_prey(prey: list[Agent], predators: list[Agent]) -> None:
    for a in prey:
        sep_x = sep_y = 0.0
        ali_x = ali_y = 0.0
        coh_x = coh_y = 0.0
        fear_x = fear_y = 0.0
        sep_count = ali_count = coh_count = fear_count = 0

        for other in prey:
            if other is a:
                continue
            dx = other.x - a.x
            dy = other.y - a.y
            dist = math.hypot(dx, dy)
            if dist < PREY_VISION:
                # Alignment
                ali_x += other.vx
                ali_y += other.vy
                ali_count += 1
                # Cohesion
                coh_x += other.x
                coh_y += other.y
                coh_count += 1
            if 0 < dist < PREY_SEP_DIST:
                sep_x -= dx / dist
                sep_y -= dy / dist
                sep_count += 1

        for pred in predators:
            dx = pred.x - a.x
            dy = pred.y - a.y
            dist = math.hypot(dx, dy)
            if dist < PREY_FEAR_DIST:
                weight = (1.0 - dist / PREY_FEAR_DIST) ** 2
                fear_x -= dx / (dist + 1e-6) * weight
                fear_y -= dy / (dist + 1e-6) * weight
                fear_count += 1

        ax_new, ay_new = a.vx, a.vy

        if sep_count:
            mag = math.hypot(sep_x, sep_y)
            if mag > 1e-6:
                ax_new += sep_x / mag * PREY_MAX_FORCE * 1.5
                ay_new += sep_y / mag * PREY_MAX_FORCE * 1.5

        if ali_count:
            tx = ali_x / ali_count
            ty = ali_y / ali_count
            fx, fy = _steer(a.x, a.y, a.vx, a.vy, a.x + tx, a.y + ty, PREY_SPEED, PREY_MAX_FORCE)
            ax_new += fx
            ay_new += fy

        if coh_count:
            tx = coh_x / coh_count
            ty = coh_y / coh_count
            fx, fy = _steer(a.x, a.y, a.vx, a.vy, tx, ty, PREY_SPEED, PREY_MAX_FORCE)
            ax_new += fx
            ay_new += fy

        if fear_count:
            mag = math.hypot(fear_x, fear_y)
            if mag > 1e-6:
                ax_new += fear_x / mag * PREY_MAX_FORCE * PREY_FEAR_WEIGHT
                ay_new += fear_y / mag * PREY_MAX_FORCE * PREY_FEAR_WEIGHT

        a.vx, a.vy = _clamp_speed(ax_new, ay_new, PREY_SPEED)
        a.x = (a.x + a.vx) % WIDTH
        a.y = (a.y + a.vy) % HEIGHT


def _update_predators(prey: list[Agent], predators: list[Agent]) -> None:
    for pred in predators:
        # Find nearest prey
        nearest_dist = float("inf")
        nearest_x, nearest_y = pred.x, pred.y
        for p in prey:
            d = math.hypot(p.x - pred.x, p.y - pred.y)
            if d < nearest_dist:
                nearest_dist = d
                nearest_x, nearest_y = p.x, p.y

        fx, fy = _steer(
            pred.x, pred.y, pred.vx, pred.vy, nearest_x, nearest_y, PRED_SPEED, PRED_MAX_FORCE
        )
        pred.vx, pred.vy = _clamp_speed(pred.vx + fx, pred.vy + fy, PRED_SPEED)
        pred.x = (pred.x + pred.vx) % WIDTH
        pred.y = (pred.y + pred.vy) % HEIGHT


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(10, 10, 25)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    py5.background(10, 10, 25, 30)
    py5.fill(10, 10, 25, 20)
    py5.no_stroke()
    py5.rect(0, 0, WIDTH, HEIGHT)

    prey = [a for a in agents if not a.is_predator]
    predators = [a for a in agents if a.is_predator]

    _update_prey(prey, predators)
    _update_predators(prey, predators)

    # Draw prey as small directional triangles
    py5.no_stroke()
    for p in prey:
        h = p.heading()
        # Check if any predator is near
        near = any(math.hypot(pr.x - p.x, pr.y - p.y) < PREY_FEAR_DIST * 0.6 for pr in predators)
        if near:
            py5.fill(255, 180, 50, 200)
        else:
            py5.fill(100, 180, 255, 180)
        py5.push_matrix()
        py5.translate(p.x, p.y)
        py5.rotate(h)
        py5.triangle(6, 0, -4, -3, -4, 3)
        py5.pop_matrix()

    # Draw predators as red diamonds
    for pred in predators:
        h = pred.heading()
        py5.fill(255, 50, 80, 230)
        py5.push_matrix()
        py5.translate(pred.x, pred.y)
        py5.rotate(h)
        py5.triangle(10, 0, -6, -5, -6, 5)
        py5.pop_matrix()

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Prey: {len(prey)} | Predators: {len(predators)}", 10, 20)


def key_pressed() -> None:
    if py5.key == "r":
        _initialize()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "predator_prey_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
