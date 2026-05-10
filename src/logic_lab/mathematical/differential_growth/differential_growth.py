import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
nodes: list[dict] = []
time_value = 0


def setup() -> None:
    py5.size(1000, 800)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    nodes.append({"x": py5.width / 2, "y": py5.height / 2})


def draw() -> None:
    global time_value
    py5.background(20)
    time_value += 1

    if time_value % 5 == 0 and len(nodes) < 200:
        idx = random.randint(0, len(nodes) - 1)
        parent = nodes[idx]
        angle = random.uniform(0, 2 * math.pi)
        new_x = parent["x"] + 5 * math.cos(angle)
        new_y = parent["y"] + 5 * math.sin(angle)
        nodes.append({"x": new_x, "y": new_y})

    py5.stroke_weight(1)
    py5.stroke(100, 200, 150)

    for i, node in enumerate(nodes[1:], 1):
        parent_idx = random.randint(0, i - 1)
        parent = nodes[parent_idx]
        py5.line(node["x"], node["y"], parent["x"], parent["y"])

    py5.fill(150, 200, 255)
    py5.stroke_weight(0)
    for node in nodes:
        py5.circle(node["x"], node["y"], 2)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "differential_growth_####.png"))


py5.run_sketch()
