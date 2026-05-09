from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time = 0.0
spread = 82.0
dispersion = True


def setup() -> None:
    py5.size(760, 380)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_packet(offset: float, hue: float, velocity: float, phase_speed: float) -> None:
    center = (py5.width * 0.18 + time * velocity + offset) % (py5.width + 260) - 130
    current_spread = spread + (time * 0.8 if dispersion else 0)
    py5.no_fill()
    py5.stroke(hue, 75, 95, 94)
    py5.stroke_weight(2.4)
    py5.begin_shape()
    for x in range(0, py5.width + 1, 3):
        envelope = math.exp(-((x - center) ** 2) / (2 * current_spread * current_spread))
        carrier = math.sin((x - center) * 0.17 - time * phase_speed)
        y = py5.height * 0.5 - carrier * envelope * 112
        py5.vertex(x, y)
    py5.end_shape()

    py5.stroke(hue, 42, 92, 34)
    py5.begin_shape()
    for x in range(0, py5.width + 1, 8):
        envelope = math.exp(-((x - center) ** 2) / (2 * current_spread * current_spread))
        py5.vertex(x, py5.height * 0.5 - envelope * 112)
    py5.end_shape()


def draw() -> None:
    global time
    time += 0.75
    py5.background(250, 18, 8)
    py5.stroke(210, 10, 74, 25)
    py5.line(0, py5.height * 0.5, py5.width, py5.height * 0.5)
    draw_packet(0, 188, 2.0, 4.3)
    draw_packet(190, 32, 1.25, 2.8)

    py5.no_stroke()
    py5.fill(42, 80, 96)
    py5.text_size(15)
    py5.text("dispersion on" if dispersion else "dispersion off", 24, 30)


def key_pressed() -> None:
    global dispersion
    if py5.key == "d":
        dispersion = not dispersion
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "wave_packet_####.png"))


py5.run_sketch()
