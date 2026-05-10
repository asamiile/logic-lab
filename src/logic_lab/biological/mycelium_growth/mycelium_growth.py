import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
network: list[dict] = []
nutrients: list[tuple] = []


def setup() -> None:
    global network, nutrients
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    network = [{"x": py5.width / 2, "y": py5.height / 2, "parent": -1}]

    for _ in range(20):
        nutrients.append((random.uniform(0, py5.width), random.uniform(0, py5.height)))


def draw() -> None:
    global network, nutrients

    for _ in range(20):
        idx = random.randint(0, len(network) - 1)
        current = network[idx]

        closest_nutrient = None
        min_dist = float("inf")

        for nutrient in nutrients:
            dist = math.sqrt((current["x"] - nutrient[0]) ** 2 + (current["y"] - nutrient[1]) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest_nutrient = nutrient

        if closest_nutrient:
            angle = math.atan2(
                closest_nutrient[1] - current["y"], closest_nutrient[0] - current["x"]
            )
            angle += random.uniform(-0.3, 0.3)

            new_x = current["x"] + 5 * math.cos(angle)
            new_y = current["y"] + 5 * math.sin(angle)

            if 0 <= new_x < py5.width and 0 <= new_y < py5.height:
                network.append({"x": new_x, "y": new_y, "parent": idx})

    py5.background(20)

    py5.stroke_weight(2)
    for node in network[1:]:
        parent = network[node["parent"]]
        py5.stroke(100, 200, 100)
        py5.line(node["x"], node["y"], parent["x"], parent["y"])

    py5.fill(150, 200, 100)
    py5.stroke_weight(0)
    for node in network:
        py5.circle(node["x"], node["y"], 2)

    py5.fill(200, 100, 100)
    for nutrient in nutrients:
        py5.circle(nutrient[0], nutrient[1], 4)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mycelium_growth_####.png"))


py5.run_sketch()
