"""
Space Colonization Algorithm.

Generates realistic tree and vascular network structures by simulating
competition between branch tips for randomly scattered "auxin" (growth
hormone) attractors. Each tip grows toward nearby attractors; once a
tip reaches an attractor, that attractor is consumed.

Algorithm (Runions et al. 2007):
    1. Scatter N attractor points in the canvas.
    2. For each attractor, find the nearest branch node.
    3. Each branch node is influenced by all attractors within a radius;
       it grows a new node one step in the average direction of those attractors.
    4. Remove attractors within kill radius of any node.
    5. Repeat until all attractors are consumed or max iterations reached.

The result is fractal-like branching that fills the attractor cloud
shape — usable for trees, root systems, coral, river deltas, or lungs.
"""

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800

SEGMENT_LEN = 6.0
INFLUENCE_RADIUS = 80.0
KILL_RADIUS = 10.0
NUM_ATTRACTORS = 600
MAX_ITER = 2000

PRESETS = {
    "tree": {"attractor_shape": "canopy", "root_y": HEIGHT - 60},
    "coral": {"attractor_shape": "cloud", "root_y": HEIGHT - 60},
    "network": {"attractor_shape": "fill", "root_y": HEIGHT // 2},
}

preset_name = "tree"


@dataclass
class Node:
    x: float
    y: float
    parent: int = -1  # index in nodes list
    depth: int = 0


nodes: list[Node]
attractors: list[tuple[float, float]]
active: bool  # still growing
iteration: int
paused: bool = False


def _scatter_attractors(shape: str) -> list[tuple[float, float]]:
    rng = random.Random(7)
    pts = []
    if shape == "canopy":
        # Elliptical crown in upper half
        cx, cy = WIDTH / 2, HEIGHT * 0.35
        rx, ry = WIDTH * 0.38, HEIGHT * 0.28
        while len(pts) < NUM_ATTRACTORS:
            x = rng.uniform(cx - rx, cx + rx)
            y = rng.uniform(cy - ry, cy + ry)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1.0:
                pts.append((x, y))
    elif shape == "cloud":
        # Several overlapping blobs
        centers = [
            (WIDTH * f, HEIGHT * g) for f, g in [(0.3, 0.3), (0.5, 0.2), (0.7, 0.35), (0.5, 0.5)]
        ]
        while len(pts) < NUM_ATTRACTORS:
            cx, cy = rng.choice(centers)
            x = rng.gauss(cx, 80)
            y = rng.gauss(cy, 80)
            if 10 < x < WIDTH - 10 and 10 < y < HEIGHT - 10:
                pts.append((x, y))
    else:  # fill
        pts = [
            (rng.uniform(20, WIDTH - 20), rng.uniform(20, HEIGHT - 20))
            for _ in range(NUM_ATTRACTORS)
        ]
    return pts


def _initialize() -> None:
    global nodes, attractors, active, iteration
    p = PRESETS[preset_name]
    nodes = [Node(x=WIDTH / 2, y=p["root_y"])]
    attractors = _scatter_attractors(p["attractor_shape"])
    active = True
    iteration = 0


def _step() -> None:
    global active, iteration
    iteration += 1
    if iteration > MAX_ITER or not attractors:
        active = False
        return

    # For each node, find attractors in influence radius
    influenced: dict[int, list[tuple[float, float]]] = {}
    to_remove = set()

    for ai, (ax, ay) in enumerate(attractors):
        # Find nearest node
        best_ni = 0
        best_d = float("inf")
        for ni, node in enumerate(nodes):
            d = math.hypot(ax - node.x, ay - node.y)
            if d < best_d:
                best_d = d
                best_ni = ni

        if best_d < KILL_RADIUS:
            to_remove.add(ai)
            continue
        if best_d < INFLUENCE_RADIUS:
            influenced.setdefault(best_ni, []).append((ax, ay))

    # Grow influenced nodes
    for ni, attr_list in influenced.items():
        node = nodes[ni]
        # Average direction toward attractors
        dx = sum(ax - node.x for ax, ay in attr_list)
        dy = sum(ay - node.y for ax, ay in attr_list)
        mag = math.hypot(dx, dy)
        if mag < 1e-6:
            continue
        dx, dy = dx / mag, dy / mag
        new_node = Node(
            x=node.x + dx * SEGMENT_LEN,
            y=node.y + dy * SEGMENT_LEN,
            parent=ni,
            depth=node.depth + 1,
        )
        nodes.append(new_node)

    # Remove consumed attractors
    attractors[:] = [a for i, a in enumerate(attractors) if i not in to_remove]

    if not influenced and not to_remove:
        active = False


def _branch_color(depth: int, max_depth: int) -> tuple[int, int, int]:
    t = depth / max(max_depth, 1)
    r = int(60 + t * 100)
    g = int(120 + t * 80)
    b = int(40 + t * 40)
    return r, g, b


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(10, 14, 8)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    if not paused and active:
        for _ in range(4):
            _step()

    py5.background(10, 14, 8)

    max_depth = max((n.depth for n in nodes), default=1)

    # Draw branches
    py5.stroke_weight(1)
    for node in nodes:
        if node.parent >= 0:
            p = nodes[node.parent]
            r, g, b = _branch_color(node.depth, max_depth)
            alpha = 200
            sw = max(0.5, 3.0 - node.depth * 0.15)
            py5.stroke(r, g, b, alpha)
            py5.stroke_weight(sw)
            py5.line(p.x, p.y, node.x, node.y)

    # Draw attractors
    py5.no_stroke()
    py5.fill(180, 220, 100, 60)
    for ax, ay in attractors:
        py5.circle(ax, ay, 3)

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    status = "growing" if active else "done"
    py5.text(
        f"Space Colonization | {preset_name} | nodes:{len(nodes)} | {status} | 1-3 R SPACE S",
        10,
        20,
    )


def key_pressed() -> None:
    global preset_name, paused
    if py5.key == "1":
        preset_name = "tree"
        _initialize()
    elif py5.key == "2":
        preset_name = "coral"
        _initialize()
    elif py5.key == "3":
        preset_name = "network"
        _initialize()
    elif py5.key == "r":
        _initialize()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"space_col_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
