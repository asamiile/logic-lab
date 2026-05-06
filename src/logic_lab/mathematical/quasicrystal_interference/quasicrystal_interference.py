from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 3
SYMMETRIES = [5, 7, 8, 10, 12]

symmetry_index = 0
frequency = 3.4
phase_offset = 0.0
animate_phase = True
threshold_mode = False
show_rings = True


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase_offset

    if animate_phase:
        phase_offset += 0.018
    field = compute_field()
    draw_field(field)
    if show_rings:
        draw_reference_rings()
    draw_info()


def compute_field() -> np.ndarray:
    symmetry = SYMMETRIES[symmetry_index]
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    values = np.zeros((rows, cols), dtype=np.float32)

    for row in range(rows):
        y = (row * PIXEL_STEP / py5.height - 0.5) * 2.0
        for col in range(cols):
            x = (col * PIXEL_STEP / py5.width - 0.5) * 2.0
            total = 0.0
            for i in range(symmetry):
                angle = py5.TWO_PI * i / symmetry
                wave = x * math.cos(angle) + y * math.sin(angle)
                total += math.cos(frequency * py5.TWO_PI * wave + phase_offset * (1 + i * 0.07))
            values[row, col] = total / symmetry

    return values


def draw_field(values: np.ndarray) -> None:
    rows, cols = values.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            v = float(values[row, col])
            if threshold_mode:
                if v > 0.18:
                    py5.fill(42, 86, 96, 100)
                elif v < -0.18:
                    py5.fill(206, 72, 42, 100)
                else:
                    py5.fill(220, 14, 95, 100)
            else:
                hue = (206 + v * 76 + SYMMETRIES[symmetry_index] * 7) % 360
                saturation = 42 + abs(v) * 48
                brightness = 42 + (v + 1) * 28
                py5.fill(hue, saturation, brightness, 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def draw_reference_rings() -> None:
    py5.no_fill()
    py5.stroke(0, 0, 100, 18)
    py5.stroke_weight(1)
    center_x = py5.width * 0.5
    center_y = py5.height * 0.5
    for radius in range(80, 340, 64):
        py5.circle(center_x, center_y, radius * 2)

    symmetry = SYMMETRIES[symmetry_index]
    for i in range(symmetry):
        angle = py5.TWO_PI * i / symmetry
        py5.line(
            center_x,
            center_y,
            center_x + math.cos(angle) * 330,
            center_y + math.sin(angle) * 330,
        )


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 640, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Quasicrystal interference | symmetry {SYMMETRIES[symmetry_index]} | frequency {frequency:.1f} | n: symmetry | +/-: frequency | t: threshold | r: rings | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global symmetry_index, frequency, threshold_mode, show_rings, animate_phase

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "quasicrystal_interference_####.png"))
    elif py5.key == "n":
        symmetry_index = (symmetry_index + 1) % len(SYMMETRIES)
    elif py5.key == "+":
        frequency = min(9.0, frequency + 0.2)
    elif py5.key == "-":
        frequency = max(1.0, frequency - 0.2)
    elif py5.key == "t":
        threshold_mode = not threshold_mode
    elif py5.key == "r":
        show_rings = not show_rings
    elif py5.key == " ":
        animate_phase = not animate_phase


py5.run_sketch()
