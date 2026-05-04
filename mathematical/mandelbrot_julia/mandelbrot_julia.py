from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 2
JULIA_PRESETS = [
    ("seahorse", complex(-0.74543, 0.11301)),
    ("spiral", complex(-0.8, 0.156)),
    ("dendrite", complex(0.0, 1.0)),
    ("rabbit", complex(-0.123, 0.745)),
    ("dust", complex(0.285, 0.01)),
]

show_julia = False
julia_index = 0
max_iterations = 96
zoom = 1.0
center_x = -0.55
center_y = 0.0
color_mode_index = 0
needs_render = True
rendered: np.ndarray | None = None


def setup() -> None:
    py5.size(760, 620)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global needs_render, rendered

    if needs_render:
        rendered = compute_escape_field()
        needs_render = False
    if rendered is not None:
        draw_rendered(rendered)
    draw_info()
    py5.no_loop()


def compute_escape_field() -> np.ndarray:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    values = np.zeros((rows, cols, 2), dtype=np.float32)

    for row in range(rows):
        y = map_to_plane(row * PIXEL_STEP, py5.height, flip=True)
        for col in range(cols):
            x = map_to_plane(col * PIXEL_STEP, py5.width, flip=False)
            if show_julia:
                z = complex(x, y)
                c = JULIA_PRESETS[julia_index][1]
            else:
                z = 0j
                c = complex(x, y)
            iteration, smooth_value = escape_iterations(z, c)
            values[row, col] = [iteration, smooth_value]

    return values


def map_to_plane(value: float, extent: float, flip: bool) -> float:
    scale = 3.2 / zoom
    if show_julia:
        mapped = (value / extent - 0.5) * scale
    else:
        mapped = (value / extent - 0.5) * scale + (center_x if not flip else center_y)
    return -mapped if flip and show_julia else mapped


def escape_iterations(z: complex, c: complex) -> tuple[int, float]:
    current = z
    for iteration in range(max_iterations):
        if current.real * current.real + current.imag * current.imag > 4:
            magnitude = abs(current)
            smooth = iteration + 1 - math.log(max(1e-9, math.log(magnitude))) / math.log(2)
            return iteration, smooth
        current = current * current + c
    return max_iterations, float(max_iterations)


def draw_rendered(values: np.ndarray) -> None:
    rows, cols, _ = values.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            iteration = int(values[row, col, 0])
            smooth = float(values[row, col, 1])
            if iteration >= max_iterations:
                py5.fill(225, 20, 6, 100)
            else:
                hue = hue_for_escape(smooth)
                brightness = 34 + 64 * min(1.0, smooth / max_iterations)
                py5.fill(hue, 78, brightness, 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def hue_for_escape(smooth: float) -> float:
    if color_mode_index == 1:
        return (34 + smooth * 12) % 360
    if color_mode_index == 2:
        return (205 + math.sin(smooth * 0.18) * 90) % 360
    return (190 + smooth * 7.5) % 360


def draw_info() -> None:
    mode_name = f"Julia {JULIA_PRESETS[julia_index][0]}" if show_julia else "Mandelbrot"
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 645, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Mandelbrot / Julia | {mode_name} | iterations {max_iterations} | zoom {zoom:.2f} | m: mode | n: Julia preset | +/-: zoom | </>: iterations | c: color | s: save",
        24,
        46,
    )


def request_render() -> None:
    global needs_render
    needs_render = True
    py5.loop()


def key_pressed() -> None:
    global show_julia, julia_index, zoom, max_iterations, color_mode_index

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mandelbrot_julia_####.png"))
    elif py5.key == "m":
        show_julia = not show_julia
        request_render()
    elif py5.key == "n":
        julia_index = (julia_index + 1) % len(JULIA_PRESETS)
        show_julia = True
        request_render()
    elif py5.key == "+":
        zoom = min(12.0, zoom * 1.25)
        request_render()
    elif py5.key == "-":
        zoom = max(0.45, zoom / 1.25)
        request_render()
    elif py5.key == "." or py5.key == ">":
        max_iterations = min(280, max_iterations + 16)
        request_render()
    elif py5.key == "," or py5.key == "<":
        max_iterations = max(24, max_iterations - 16)
        request_render()
    elif py5.key == "c":
        color_mode_index = (color_mode_index + 1) % 3
        request_render()


py5.run_sketch()
