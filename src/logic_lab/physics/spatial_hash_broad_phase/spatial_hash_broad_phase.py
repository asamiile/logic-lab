from pathlib import Path
from random import Random

import py5
from logic_lab.shared.physics2d import (
    CircleBody,
    SpatialHash,
    Vec2,
    resolve_bounds,
    resolve_circle_collision,
)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(5)
bodies: list[CircleBody] = []
grid = SpatialHash(48)
pair_count = 0


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    for _ in range(170):
        radius = rng.uniform(3, 8)
        bodies.append(
            CircleBody(
                Vec2(rng.uniform(20, 620), rng.uniform(20, 340)),
                Vec2(rng.uniform(-70, 70), rng.uniform(-55, 55)),
                radius,
                mass=radius,
            )
        )
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global pair_count
    py5.background(250)
    grid.clear()
    for i, body in enumerate(bodies):
        body.step(1 / 60)
        resolve_bounds(body, py5.width, py5.height, restitution=0.95)
        grid.insert_circle(i, body.pos, body.radius)
    pairs = grid.potential_pairs()
    pair_count = len(pairs)
    for a_idx, b_idx in pairs:
        resolve_circle_collision(bodies[a_idx], bodies[b_idx])
    py5.stroke(225)
    for x in range(0, py5.width, int(grid.cell_size)):
        py5.line(x, 0, x, py5.height)
    for y in range(0, py5.height, int(grid.cell_size)):
        py5.line(0, y, py5.width, y)
    py5.no_stroke()
    py5.fill(40, 120, 190, 160)
    for body in bodies:
        py5.circle(body.pos.x, body.pos.y, body.radius * 2)
    py5.fill(20)
    py5.text(f"bodies: {len(bodies)}  broad-phase pairs: {pair_count}", 16, 28)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spatial_hash_broad_phase_####.png"))


py5.run_sketch()
