from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

mode = 3
phase = 0.0
show_modes = True


def setup() -> None:
    py5.size(720, 420)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_string(y_base: float, current_mode: int, alpha: float, weight: float) -> None:
    amplitude = 120 / math.sqrt(current_mode)
    py5.no_fill()
    py5.stroke(38 + current_mode * 22, 78, 94, alpha)
    py5.stroke_weight(weight)
    py5.begin_shape()
    for x in range(54, py5.width - 53, 4):
        amount = (x - 54) / (py5.width - 108)
        y = y_base + math.sin(math.pi * current_mode * amount) * math.cos(phase) * amplitude
        py5.vertex(x, y)
    py5.end_shape()


def draw() -> None:
    global phase
    phase += 0.045
    py5.background(224, 22, 11)

    py5.stroke(220, 8, 82, 30)
    py5.stroke_weight(1)
    for i in range(mode + 1):
        x = 54 + (py5.width - 108) * i / mode
        py5.line(x, 72, x, py5.height - 72)

    if show_modes:
        for sub_mode in range(1, mode):
            draw_string(py5.height * 0.5, sub_mode, 18, 1)

    draw_string(py5.height * 0.5, mode, 100, 3)

    py5.no_stroke()
    py5.fill(44, 78, 94)
    py5.circle(54, py5.height * 0.5, 11)
    py5.circle(py5.width - 54, py5.height * 0.5, 11)
    py5.text_size(16)
    py5.text(f"mode {mode}", 24, 32)


def key_pressed() -> None:
    global mode, show_modes
    if py5.key in ("+", "="):
        mode = min(9, mode + 1)
    elif py5.key == "-":
        mode = max(1, mode - 1)
    elif py5.key == "v":
        show_modes = not show_modes
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "standing_wave_####.png"))


py5.run_sketch()
