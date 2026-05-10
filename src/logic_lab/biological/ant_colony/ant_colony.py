import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
ants: list[dict] = []
pheromone_map: list[list[float]] = []


def setup() -> None:
    global ants, pheromone_map
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    for _ in range(50):
        ants.append(
            {
                "x": py5.width / 2,
                "y": py5.height / 2,
                "angle": random.uniform(0, 2 * math.pi),
                "food": False,
            }
        )

    grid_size = 50
    pheromone_map = [[0.0] * grid_size for _ in range(grid_size)]


def draw() -> None:
    global pheromone_map
    py5.background(20)

    grid_x, grid_y = len(pheromone_map[0]), len(pheromone_map)
    scale_x, scale_y = py5.width / grid_x, py5.height / grid_y

    for ant in ants:
        gx, gy = int(ant["x"] / scale_x), int(ant["y"] / scale_y)

        if 0 <= gx < grid_x and 0 <= gy < grid_y:
            pheromone_map[gy][gx] += 1

            if pheromone_map[gy][gx] > 10:
                ant["food"] = True

        if ant["food"]:
            ant["angle"] += random.uniform(-0.3, 0.3)
        else:
            best_angle = ant["angle"]
            max_pheromone = 0

            for test_angle in [ant["angle"] - 0.5, ant["angle"], ant["angle"] + 0.5]:
                tx = int((ant["x"] + 20 * math.cos(test_angle)) / scale_x)
                ty = int((ant["y"] + 20 * math.sin(test_angle)) / scale_y)

                if 0 <= tx < grid_x and 0 <= ty < grid_y:
                    if pheromone_map[ty][tx] > max_pheromone:
                        max_pheromone = pheromone_map[ty][tx]
                        best_angle = test_angle

            ant["angle"] = best_angle

        ant["x"] += 3 * math.cos(ant["angle"])
        ant["y"] += 3 * math.sin(ant["angle"])

        if ant["x"] < 0:
            ant["x"] = py5.width
        if ant["x"] > py5.width:
            ant["x"] = 0
        if ant["y"] < 0:
            ant["y"] = py5.height
        if ant["y"] > py5.height:
            ant["y"] = 0

        py5.fill(255, 150, 100) if ant["food"] else py5.fill(100, 150, 255)
        py5.stroke_weight(0)
        py5.circle(ant["x"], ant["y"], 2)

    for pheromone_map[y][x] in enumerate(pheromone_map):
        pheromone_map[y][x] *= 0.95

    for y in range(len(pheromone_map)):
        for x in range(len(pheromone_map[0])):
            val = int(pheromone_map[y][x] * 2)
            if val > 0:
                py5.fill(val, 100, 200, min(val, 255))
                py5.stroke_weight(0)
                py5.rect(x * scale_x, y * scale_y, scale_x, scale_y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ant_colony_####.png"))


py5.run_sketch()
