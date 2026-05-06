from __future__ import annotations

import cmath
import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 3
FUNCTIONS = ["z^2 - 1", "1 / z", "sin(z)", "mobius", "z^3 - z"]

function_index = 0
zoom = 1.0
show_grid = True
show_phase_lines = True
animate_params = True


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    t = py5.frame_count * 0.016 if animate_params else 0.0
    draw_domain(t)
    if show_grid:
        draw_complex_grid()
    draw_info()


def draw_domain(t: float) -> None:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    pixels = np.zeros((rows, cols, 3), dtype=np.float32)

    for row in range(rows):
        y = map_to_plane(row * PIXEL_STEP, py5.height, flip=True)
        for col in range(cols):
            x = map_to_plane(col * PIXEL_STEP, py5.width, flip=False)
            value = complex_function(complex(x, y), t)
            hue, saturation, brightness = color_for_complex(value)
            if show_phase_lines:
                brightness *= phase_line_factor(value)
                brightness *= magnitude_ring_factor(value)
            pixels[row, col] = [hue, saturation, brightness]

    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            h, s, b = pixels[row, col]
            py5.fill(float(h), float(s), float(b), 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def map_to_plane(value: float, extent: float, flip: bool) -> float:
    centered = (value / extent - 0.5) * 4.0 / zoom
    return -centered if flip else centered


def complex_function(z: complex, t: float) -> complex:
    name = FUNCTIONS[function_index]
    try:
        if name == "1 / z":
            return 1 / z
        if name == "sin(z)":
            return cmath.sin(z)
        if name == "mobius":
            a = complex(0.6 + 0.2 * math.sin(t), 0.45)
            b = complex(-0.35, 0.22 + 0.15 * math.cos(t * 0.8))
            c = complex(0.18, -0.38)
            d = complex(0.8, 0.15 * math.sin(t * 0.7))
            return (a * z + b) / (c * z + d)
        if name == "z^3 - z":
            return z**3 - z
        return z * z - 1
    except ZeroDivisionError:
        return complex(float("inf"), float("inf"))


def color_for_complex(value: complex) -> tuple[float, float, float]:
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        return 0, 0, 0

    phase = math.atan2(value.imag, value.real)
    magnitude = abs(value)
    hue = (math.degrees(phase) + 360) % 360
    saturation = 78
    brightness = 58 + 38 * (1 - 1 / (1 + magnitude))
    brightness *= 0.78 + 0.22 * math.cos(math.log1p(magnitude) * math.tau)
    return hue, saturation, max(8, min(100, brightness))


def phase_line_factor(value: complex) -> float:
    if value == 0 or not math.isfinite(value.real) or not math.isfinite(value.imag):
        return 1.0
    phase = (math.atan2(value.imag, value.real) + math.pi) / math.tau
    distance = abs((phase * 18) % 1 - 0.5) * 2
    return 0.42 + 0.58 * smoothstep(0.08, 0.22, distance)


def magnitude_ring_factor(value: complex) -> float:
    magnitude = abs(value)
    if not math.isfinite(magnitude):
        return 1.0
    ring = abs((math.log1p(magnitude) * 5.5) % 1 - 0.5) * 2
    return 0.62 + 0.38 * smoothstep(0.05, 0.18, ring)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    amount = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return amount * amount * (3 - 2 * amount)


def draw_complex_grid() -> None:
    py5.stroke(0, 0, 100, 24)
    py5.stroke_weight(1)
    spacing = py5.width * zoom / 4
    center = py5.width * 0.5
    for i in range(-4, 5):
        x = center + i * spacing
        y = center + i * spacing
        py5.line(x, 0, x, py5.height)
        py5.line(0, y, py5.width, y)

    py5.stroke(0, 0, 100, 58)
    py5.stroke_weight(1.8)
    py5.line(center, 0, center, py5.height)
    py5.line(0, center, py5.width, center)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 610, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Complex domain coloring | f: {FUNCTIONS[function_index]} | zoom {zoom:.1f} | n: function | +/-: zoom | g: grid | l: lines | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global function_index, zoom, show_grid, show_phase_lines, animate_params

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "complex_domain_coloring_####.png"))
    elif py5.key == "n":
        function_index = (function_index + 1) % len(FUNCTIONS)
    elif py5.key == "+":
        zoom = min(4.0, zoom * 1.18)
    elif py5.key == "-":
        zoom = max(0.35, zoom / 1.18)
    elif py5.key == "g":
        show_grid = not show_grid
    elif py5.key == "l":
        show_phase_lines = not show_phase_lines
    elif py5.key == " ":
        animate_params = not animate_params


py5.run_sketch()
