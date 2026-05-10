from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
frequency = 0.02
line_spacing = 12


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    freq = frequency + 0.01 * math.sin(time_value)
    rotation = time_value * 20

    py5.push_matrix()
    py5.rotate(math.radians(rotation))

    width, height = 400, 320

    for y in range(-height, height + 1, line_spacing):
        for x in range(-width, width, line_spacing):
            brightness = (math.sin(x * freq) + math.sin(y * freq)) / 2
            brightness = (brightness + 1) / 2

            spacing = line_spacing * (0.3 + 0.7 * brightness)
            hue = (brightness * 120 + time_value * 50) % 360
            py5.stroke(hue, 60, 100)
            py5.stroke_weight(1.5)

            x1 = x - spacing * 2
            x2 = x + spacing * 2
            py5.line(x1, y, x2, y)

    py5.pop_matrix()

    py5.push_matrix()
    py5.rotate(math.radians(rotation + 45))

    for y in range(-height, height + 1, line_spacing * 1.5):
        for x in range(-width, width, line_spacing * 1.5):
            brightness = (math.sin(x * freq * 0.7) + math.sin(y * freq * 0.7)) / 2
            brightness = (brightness + 1) / 2

            if brightness > 0.4:
                spacing = line_spacing * 0.7 * (1.0 - brightness)
                hue = (brightness * 120 + 180 + time_value * 50) % 360
                py5.stroke(hue, 50, 90)
                py5.stroke_weight(1)

                x1 = x - spacing * 2
                x2 = x + spacing * 2
                py5.line(x1, y, x2, y)

    py5.pop_matrix()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hatching_patterns_####.png"))


py5.run_sketch()
