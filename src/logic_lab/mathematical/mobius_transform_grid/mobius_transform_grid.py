from __future__ import annotations

import cmath
import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    ("bend", complex(1.0, 0.15), complex(0.25, 0.2), complex(0.22, -0.28), complex(1.0, 0.0)),
    ("twist", complex(0.8, 0.45), complex(-0.3, 0.25), complex(0.18, 0.42), complex(0.9, -0.2)),
    ("lens", complex(1.0, 0.0), complex(0.0, 0.0), complex(0.55, 0.0), complex(1.0, 0.0)),
    ("spiral", complex(0.75, 0.55), complex(0.18, -0.34), complex(-0.22, 0.34), complex(1.0, 0.0)),
]

preset_index = 0
show_source_grid = False
show_unit_circle = True
animate_coefficients = True
phase = 0.0


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase

    if animate_coefficients:
        phase += 0.015

    py5.background(218, 14, 96)
    py5.translate(py5.width * 0.5, py5.height * 0.5)

    if show_source_grid:
        draw_source_grid()
    if show_unit_circle:
        draw_transformed_unit_circle()
    draw_transformed_grid()

    py5.reset_matrix()
    draw_info()


def mobius(z: complex) -> complex | None:
    _, a, b, c, d = PRESETS[preset_index]
    wobble = complex(math.cos(phase) * 0.08, math.sin(phase * 0.7) * 0.08)
    c = c + wobble if animate_coefficients else c
    denominator = c * z + d
    if abs(denominator) < 1e-5:
        return None
    return (a * z + b) / denominator


def to_screen(z: complex) -> tuple[float, float]:
    scale = 170
    return z.real * scale, -z.imag * scale


def draw_source_grid() -> None:
    py5.stroke(220, 24, 24, 18)
    py5.stroke_weight(1)
    for value in [i * 0.4 for i in range(-5, 6)]:
        x1, y1 = to_screen(complex(value, -2.0))
        x2, y2 = to_screen(complex(value, 2.0))
        py5.line(x1, y1, x2, y2)
        x1, y1 = to_screen(complex(-2.0, value))
        x2, y2 = to_screen(complex(2.0, value))
        py5.line(x1, y1, x2, y2)


def draw_transformed_grid() -> None:
    values = [i * 0.25 for i in range(-8, 9)]
    for i, value in enumerate(values):
        hue = (198 + i * 7) % 360
        draw_transformed_line([complex(value, t) for t in sample_range(-2.1, 2.1, 190)], hue)
        draw_transformed_line(
            [complex(t, value) for t in sample_range(-2.1, 2.1, 190)], (hue + 46) % 360
        )


def draw_transformed_unit_circle() -> None:
    points = [cmath.exp(1j * py5.TWO_PI * i / 240) for i in range(241)]
    py5.stroke(38, 88, 96, 94)
    py5.stroke_weight(2.6)
    draw_complex_polyline(points)


def draw_transformed_line(points: list[complex], hue: float) -> None:
    py5.stroke(hue, 70, 44, 72)
    py5.stroke_weight(1.25)
    draw_complex_polyline(points)


def draw_complex_polyline(points: list[complex]) -> None:
    current: list[tuple[float, float]] = []
    for point in points:
        transformed = mobius(point)
        if transformed is None or abs(transformed) > 4.5:
            flush_polyline(current)
            current = []
            continue
        current.append(to_screen(transformed))
    flush_polyline(current)


def flush_polyline(points: list[tuple[float, float]]) -> None:
    if len(points) < 2:
        return
    py5.no_fill()
    py5.begin_shape()
    for x, y in points:
        py5.vertex(x, y)
    py5.end_shape()


def sample_range(start: float, end: float, count: int) -> list[float]:
    return [start + (end - start) * i / max(1, count - 1) for i in range(count)]


def draw_info() -> None:
    name = PRESETS[preset_index][0]
    py5.no_stroke()
    py5.fill(218, 24, 12, 90)
    py5.rect(14, 14, 625, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Mobius transform grid | {name} | n: preset | g: source grid | u: unit circle | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, show_source_grid, show_unit_circle, animate_coefficients

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mobius_transform_grid_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
    elif py5.key == "g":
        show_source_grid = not show_source_grid
    elif py5.key == "u":
        show_unit_circle = not show_unit_circle
    elif py5.key == " ":
        animate_coefficients = not animate_coefficients


py5.run_sketch()
