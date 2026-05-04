from __future__ import annotations

from pathlib import Path
import cmath
import math

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 2
PRESETS = ["z^3 - 1", "z^4 - 1", "z^5 - z", "z^3 - 2z + 2"]

preset_index = 0
zoom = 1.0
offset_x = 0.0
offset_y = 0.0
max_iterations = 36
needs_render = True
result_image: np.ndarray | None = None


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global needs_render, result_image

    if needs_render:
        result_image = compute_fractal()
        needs_render = False
    if result_image is not None:
        draw_image(result_image)
    draw_info()
    py5.no_loop()


def compute_fractal() -> np.ndarray:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    pixels = np.zeros((rows, cols, 3), dtype=np.float32)

    roots = preset_roots()
    for row in range(rows):
        y = map_to_plane(row * PIXEL_STEP, py5.height, flip=True) + offset_y
        for col in range(cols):
            x = map_to_plane(col * PIXEL_STEP, py5.width, flip=False) + offset_x
            root_index, iterations, residual = newton_solve(complex(x, y), roots)
            pixels[row, col] = color_for_result(root_index, iterations, residual, len(roots))

    return pixels


def map_to_plane(value: float, extent: float, flip: bool) -> float:
    mapped = (value / extent - 0.5) * 4.0 / zoom
    return -mapped if flip else mapped


def preset_roots() -> list[complex]:
    name = PRESETS[preset_index]
    if name == "z^4 - 1":
        return [1, 1j, -1, -1j]
    if name == "z^5 - z":
        return [0, 1, -1, 1j, -1j]
    if name == "z^3 - 2z + 2":
        return [
            complex(-1.7692923542386314, 0),
            complex(0.8846461771193157, 0.5897428050222054),
            complex(0.8846461771193157, -0.5897428050222054),
        ]
    return [cmath.exp(2j * math.pi * i / 3) for i in range(3)]


def polynomial(z: complex) -> complex:
    name = PRESETS[preset_index]
    if name == "z^4 - 1":
        return z**4 - 1
    if name == "z^5 - z":
        return z**5 - z
    if name == "z^3 - 2z + 2":
        return z**3 - 2 * z + 2
    return z**3 - 1


def derivative(z: complex) -> complex:
    name = PRESETS[preset_index]
    if name == "z^4 - 1":
        return 4 * z**3
    if name == "z^5 - z":
        return 5 * z**4 - 1
    if name == "z^3 - 2z + 2":
        return 3 * z**2 - 2
    return 3 * z**2


def newton_solve(z: complex, roots: list[complex]) -> tuple[int, int, float]:
    current = z
    for iteration in range(max_iterations):
        deriv = derivative(current)
        if abs(deriv) < 1e-9:
            break
        current = current - polynomial(current) / deriv
        for i, root in enumerate(roots):
            distance = abs(current - root)
            if distance < 1e-5:
                return i, iteration, distance

    distances = [abs(current - root) for root in roots]
    root_index = int(np.argmin(distances))
    return root_index, max_iterations, distances[root_index]


def color_for_result(root_index: int, iterations: int, residual: float, root_count: int) -> tuple[float, float, float]:
    hue = (root_index * 360 / root_count + iterations * 2.4) % 360
    convergence = 1 - iterations / max(1, max_iterations)
    edge = min(1.0, math.log1p(residual * 1000) * 0.28)
    saturation = 72 + edge * 20
    brightness = 28 + convergence * 68
    return hue, saturation, brightness


def draw_image(pixels: np.ndarray) -> None:
    rows, cols, _ = pixels.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            h, s, b = pixels[row, col]
            py5.fill(float(h), float(s), float(b), 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 620, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Newton fractal | {PRESETS[preset_index]} | zoom {zoom:.2f} | iterations {max_iterations} | n: function | +/-: zoom | </>: iterations | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, zoom, max_iterations, needs_render

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "newton_fractal_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        needs_render = True
        py5.loop()
    elif py5.key == "+":
        zoom = min(8.0, zoom * 1.25)
        needs_render = True
        py5.loop()
    elif py5.key == "-":
        zoom = max(0.4, zoom / 1.25)
        needs_render = True
        py5.loop()
    elif py5.key == "." or py5.key == ">":
        max_iterations = min(80, max_iterations + 4)
        needs_render = True
        py5.loop()
    elif py5.key == "," or py5.key == "<":
        max_iterations = max(8, max_iterations - 4)
        needs_render = True
        py5.loop()


py5.run_sketch()
