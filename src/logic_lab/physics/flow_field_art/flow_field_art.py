import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
particles: list[dict] = []
time_value = 0.0


def setup() -> None:
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    for _ in range(500):
        particles.append(
            {"x": random.uniform(0, py5.width), "y": random.uniform(0, py5.height), "trail": []}
        )


def draw() -> None:
    global time_value
    py5.background(20)
    time_value += 0.01

    for particle in particles:
        angle = (
            math.sin(particle["x"] * 0.01 + time_value)
            * math.cos(particle["y"] * 0.01 + time_value)
            * math.pi
            * 2
        )
        speed = 3

        particle["x"] += math.cos(angle) * speed
        particle["y"] += math.sin(angle) * speed

        if particle["x"] < 0:
            particle["x"] = py5.width
        if particle["x"] > py5.width:
            particle["x"] = 0
        if particle["y"] < 0:
            particle["y"] = py5.height
        if particle["y"] > py5.height:
            particle["y"] = 0

        particle["trail"].append((particle["x"], particle["y"]))
        if len(particle["trail"]) > 50:
            particle["trail"].pop(0)

        hue = int(particle["x"] + particle["y"]) % 256
        py5.stroke(hue, 150, 255 - hue)
        py5.stroke_weight(1)

        for i in range(len(particle["trail"]) - 1):
            py5.line(
                particle["trail"][i][0],
                particle["trail"][i][1],
                particle["trail"][i + 1][0],
                particle["trail"][i + 1][1],
            )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flow_field_art_####.png"))


py5.run_sketch()
