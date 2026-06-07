"""
Ant Colony Pheromone Trails.

Simulates ant colony foraging behavior using pheromone stigmergy —
ants deposit chemical trails that guide other ants toward food sources.
Over time, the shortest paths are reinforced while longer paths fade.

Behavior rules:
    - Ants wander and follow pheromone gradients with bias toward food.
    - On finding food, they return to hive depositing a strong trail.
    - Pheromone evaporates each frame, creating emergent path optimization.
    - Trail patterns produce organic, flowing line art.
"""

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
NUM_ANTS = 200
NUM_FOOD = 5
PHEROMONE_EVAPORATION = 0.995  # Multiplier per frame (< 1 = evaporation)
PHEROMONE_DEPOSIT = 10.0
PHEROMONE_DEPOSIT_FOOD = 30.0
SENSOR_ANGLE = math.radians(30)
SENSOR_DIST = 15.0
TURN_SPEED = math.radians(25)
SPEED = 2.5
HIVE_RADIUS = 20.0
FOOD_RADIUS = 18.0


@dataclass
class FoodSource:
    x: float
    y: float
    amount: float = 200.0


@dataclass
class Ant:
    x: float
    y: float
    angle: float
    has_food: bool = False


pheromone_home: np.ndarray  # Trail toward home
pheromone_food: np.ndarray  # Trail toward food
ants: list[Ant]
foods: list[FoodSource]
hive_x: float
hive_y: float


def _sense(grid: np.ndarray, x: float, y: float, angle: float) -> tuple[float, float, float]:
    """Sample pheromone at left, center, right sensor positions."""

    def sample(a: float) -> float:
        sx = int(x + math.cos(a) * SENSOR_DIST) % WIDTH
        sy = int(y + math.sin(a) * SENSOR_DIST) % HEIGHT
        return float(grid[sy, sx])

    return sample(angle - SENSOR_ANGLE), sample(angle), sample(angle + SENSOR_ANGLE)


def _initialize() -> None:
    global pheromone_home, pheromone_food, ants, foods, hive_x, hive_y

    hive_x = WIDTH / 2.0
    hive_y = HEIGHT / 2.0
    pheromone_home = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    pheromone_food = np.zeros((HEIGHT, WIDTH), dtype=np.float32)

    rng = random.Random(42)
    ants = [
        Ant(
            x=hive_x + rng.uniform(-10, 10),
            y=hive_y + rng.uniform(-10, 10),
            angle=rng.uniform(0, math.tau),
        )
        for _ in range(NUM_ANTS)
    ]

    foods = []
    rng2 = random.Random(7)
    for _ in range(NUM_FOOD):
        foods.append(
            FoodSource(
                x=rng2.uniform(80, WIDTH - 80),
                y=rng2.uniform(80, HEIGHT - 80),
            )
        )


def _update_ants() -> None:
    for ant in ants:
        # Sense relevant pheromone
        grid = pheromone_food if not ant.has_food else pheromone_home
        left, center, right = _sense(grid, ant.x, ant.y, ant.angle)

        if center > left and center > right:
            pass  # Go straight
        elif left > right:
            ant.angle -= TURN_SPEED
        elif right > left:
            ant.angle += TURN_SPEED
        else:
            ant.angle += random.uniform(-TURN_SPEED, TURN_SPEED)

        # Add random wander
        ant.angle += random.uniform(-0.1, 0.1)

        ant.x = (ant.x + math.cos(ant.angle) * SPEED) % WIDTH
        ant.y = (ant.y + math.sin(ant.angle) * SPEED) % HEIGHT

        gx = int(ant.x) % WIDTH
        gy = int(ant.y) % HEIGHT

        # Deposit pheromone
        if ant.has_food:
            pheromone_food[gy, gx] = min(pheromone_food[gy, gx] + PHEROMONE_DEPOSIT_FOOD, 255.0)
        else:
            pheromone_home[gy, gx] = min(pheromone_home[gy, gx] + PHEROMONE_DEPOSIT, 255.0)

        # Check food pickup
        if not ant.has_food:
            for food in foods:
                if food.amount > 0 and math.hypot(ant.x - food.x, ant.y - food.y) < FOOD_RADIUS:
                    ant.has_food = True
                    food.amount -= 1
                    ant.angle += math.pi  # Turn around
                    break

        # Check home return
        if ant.has_food and math.hypot(ant.x - hive_x, ant.y - hive_y) < HIVE_RADIUS:
            ant.has_food = False
            ant.angle += math.pi


def _evaporate() -> None:
    pheromone_home[:] *= PHEROMONE_EVAPORATION
    pheromone_food[:] *= PHEROMONE_EVAPORATION


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(15, 10, 20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    py5.background(15, 10, 20)

    _update_ants()
    _evaporate()

    # Draw pheromone home (warm amber)
    for y in range(0, HEIGHT, 2):
        for x in range(0, WIDTH, 2):
            ph = pheromone_home[y, x]
            pf = pheromone_food[y, x]
            if ph > 1.0 or pf > 1.0:
                r = min(255, int(ph * 1.2 + pf * 0.3))
                g = min(255, int(ph * 0.6 + pf * 0.9))
                b = min(255, int(ph * 0.1 + pf * 0.5))
                py5.stroke(r, g, b, 180)
                py5.point(x, y)

    # Draw hive
    py5.no_stroke()
    py5.fill(255, 200, 50, 220)
    py5.circle(hive_x, hive_y, HIVE_RADIUS * 2)

    # Draw food sources
    for food in foods:
        alpha = int(min(255, food.amount * 1.2))
        py5.fill(50, 200, 80, alpha)
        py5.circle(food.x, food.y, FOOD_RADIUS * 2)

    # Draw ants
    for ant in ants:
        py5.stroke(255, 100 if ant.has_food else 220, 50 if ant.has_food else 180, 200)
        py5.stroke_weight(2)
        tip_x = ant.x + math.cos(ant.angle) * 4
        tip_y = ant.y + math.sin(ant.angle) * 4
        py5.line(ant.x, ant.y, tip_x, tip_y)

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    food_left = sum(int(f.amount) for f in foods)
    carrying = sum(1 for a in ants if a.has_food)
    py5.text(f"Food left: {food_left} | Carrying: {carrying}/{NUM_ANTS}", 10, 20)


def key_pressed() -> None:
    if py5.key == "r":
        _initialize()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ant_colony_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
