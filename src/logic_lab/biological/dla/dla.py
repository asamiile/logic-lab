"""
Diffusion-Limited Aggregation (DLA).

Particles perform random walks from the edge of the canvas until they
contact the growing aggregate, where they stick permanently. The result
is a fractal cluster with a branching, dendritic form — resembling
snowflakes, coral, lightning, or mineral deposits.

Variants:
    radial   — aggregate grows outward from a center seed
    linear   — particles fall from the top toward a bottom boundary
    circular — seed is a ring; growth fills inward
"""

import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 700
HEIGHT = 700

PRESETS = {
    "radial": {"spawn": "edge", "seed": "center"},
    "linear": {"spawn": "top", "seed": "bottom"},
    "circular": {"spawn": "center", "seed": "ring"},
}

preset_name = "radial"

# Aggregate stored as a set of (x, y) integer pixels for fast neighbour lookup
aggregate: set[tuple[int, int]]
# Active walkers
walkers: list[list[int]]  # each is [x, y]
MAX_WALKERS = 80
STEP = 1
SPAWN_BATCH = 8
paused = False
age_map: dict[tuple[int, int], int]  # pixel → step it joined
total_steps = 0


def _neighbors(x: int, y: int) -> list[tuple[int, int]]:
    return [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
        (x + 1, y + 1),
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
    ]


def _touches_aggregate(x: int, y: int) -> bool:
    return any(n in aggregate for n in _neighbors(x, y))


def _spawn_walker() -> list[int]:
    rng = random.Random()
    p = PRESETS[preset_name]
    if p["spawn"] == "edge":
        angle = rng.uniform(0, math.tau)
        r = min(WIDTH, HEIGHT) / 2 - 2
        x = int(WIDTH / 2 + r * math.cos(angle))
        y = int(HEIGHT / 2 + r * math.sin(angle))
    elif p["spawn"] == "top":
        x = rng.randint(0, WIDTH - 1)
        y = 2
    else:  # center
        x = WIDTH // 2 + rng.randint(-10, 10)
        y = HEIGHT // 2 + rng.randint(-10, 10)
    return [x, y]


def _initialize() -> None:
    global aggregate, walkers, age_map, total_steps
    aggregate = set()
    age_map = {}
    walkers = []
    total_steps = 0

    p = PRESETS[preset_name]
    cx, cy = WIDTH // 2, HEIGHT // 2

    if p["seed"] == "center":
        aggregate.add((cx, cy))
        age_map[(cx, cy)] = 0
    elif p["seed"] == "bottom":
        for x in range(0, WIDTH, 2):
            aggregate.add((x, HEIGHT - 3))
            age_map[(x, HEIGHT - 3)] = 0
    elif p["seed"] == "ring":
        r = 60
        for i in range(200):
            angle = i / 200 * math.tau
            px = int(cx + r * math.cos(angle))
            py = int(cy + r * math.sin(angle))
            aggregate.add((px, py))
            age_map[(px, py)] = 0


def _step() -> None:
    global total_steps
    total_steps += 1

    # Spawn new walkers
    while len(walkers) < MAX_WALKERS:
        walkers.append(_spawn_walker())

    # Move walkers
    stuck = []
    for w in walkers:
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        w[0] = max(0, min(WIDTH - 1, w[0] + dx))
        w[1] = max(0, min(HEIGHT - 1, w[1] + dy))

        if _touches_aggregate(w[0], w[1]):
            pt = (w[0], w[1])
            aggregate.add(pt)
            age_map[pt] = total_steps
            stuck.append(w)

    for w in stuck:
        walkers.remove(w)


def _age_color(age: int, max_age: int) -> tuple[int, int, int]:
    t = age / max(max_age, 1)
    # Deep blue (old) → cyan → white (new)
    r = int(t * 200)
    g = int(60 + t * 195)
    b = int(180 + t * 75)
    return r, g, b


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(8, 8, 18)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    if not paused:
        for _ in range(12):
            _step()

    py5.background(8, 8, 18)

    max_age = total_steps or 1

    # Draw aggregate
    py5.stroke_weight(1)
    py5.no_fill()
    for (ax, ay), age in age_map.items():
        r, g, b = _age_color(age, max_age)
        py5.stroke(r, g, b, 220)
        py5.point(ax, ay)

    # Draw walkers
    py5.stroke(255, 120, 60, 140)
    py5.stroke_weight(2)
    for w in walkers:
        py5.point(w[0], w[1])

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"DLA | {preset_name} | {len(aggregate)} pts | 1-3=preset R=reset SPACE=pause S=save",
        10,
        20,
    )


def key_pressed() -> None:
    global preset_name, paused
    if py5.key == "1":
        preset_name = "radial"
        _initialize()
    elif py5.key == "2":
        preset_name = "linear"
        _initialize()
    elif py5.key == "3":
        preset_name = "circular"
        _initialize()
    elif py5.key == "r":
        _initialize()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"dla_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
