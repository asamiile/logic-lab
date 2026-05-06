from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    ("classic", 6, 71),
    ("lace", 5, 97),
    ("star net", 7, 89),
    ("woven", 8, 53),
    ("dense", 11, 79),
]

preset_index = 0
show_rose_curve = True
show_maurer_lines = True
animate_step = True
step_offset = 0.0


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global step_offset

    py5.background(216, 14, 96)
    name, petal_count, base_step = PRESETS[preset_index]
    if animate_step:
        step_offset += 0.018
    step_degrees = base_step + math.sin(step_offset) * 5.0

    py5.translate(py5.width * 0.5, py5.height * 0.54)
    if show_rose_curve:
        draw_rose_curve(petal_count)
    if show_maurer_lines:
        draw_maurer_lines(petal_count, step_degrees)
    draw_axes_hint()
    py5.reset_matrix()
    draw_info(name, petal_count, step_degrees)


def rose_point(petal_count: int, theta: float, scale: float) -> tuple[float, float]:
    radius = math.sin(petal_count * theta) * scale
    return math.cos(theta) * radius, math.sin(theta) * radius


def draw_rose_curve(petal_count: int) -> None:
    scale = py5.width * 0.38
    py5.no_fill()
    py5.stroke(202, 70, 46, 34)
    py5.stroke_weight(7)
    py5.begin_shape()
    for i in range(1441):
        theta = py5.TWO_PI * i / 1440
        x, y = rose_point(petal_count, theta, scale)
        py5.vertex(x, y)
    py5.end_shape()

    py5.stroke(34, 86, 96, 90)
    py5.stroke_weight(1.8)
    py5.begin_shape()
    for i in range(1441):
        theta = py5.TWO_PI * i / 1440
        x, y = rose_point(petal_count, theta, scale)
        py5.vertex(x, y)
    py5.end_shape()


def draw_maurer_lines(petal_count: int, step_degrees: float) -> None:
    scale = py5.width * 0.38
    points = []
    for i in range(361):
        theta = math.radians(i * step_degrees)
        points.append(rose_point(petal_count, theta, scale))

    py5.no_fill()
    py5.stroke_weight(1.05)
    py5.begin_shape()
    for i, (x, y) in enumerate(points):
        hue = (188 + i * 132 / max(1, len(points))) % 360
        py5.stroke(hue, 62, 36 + i * 54 / max(1, len(points)), 78)
        py5.vertex(x, y)
    py5.end_shape()

    py5.no_stroke()
    for i in range(0, len(points), 12):
        x, y = points[i]
        py5.fill((190 + i) % 360, 72, 92, 88)
        py5.circle(x, y, 4)


def draw_axes_hint() -> None:
    py5.stroke(220, 16, 28, 18)
    py5.stroke_weight(1)
    py5.line(-py5.width * 0.42, 0, py5.width * 0.42, 0)
    py5.line(0, -py5.height * 0.42, 0, py5.height * 0.42)


def draw_info(name: str, petal_count: int, step_degrees: float) -> None:
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 615, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Maurer rose | {name} n={petal_count} step={step_degrees:.1f} | n: preset | r: rose | l: lines | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, show_rose_curve, show_maurer_lines, animate_step, step_offset

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "maurer_rose_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        step_offset = 0.0
    elif py5.key == "r":
        show_rose_curve = not show_rose_curve
    elif py5.key == "l":
        show_maurer_lines = not show_maurer_lines
    elif py5.key == " ":
        animate_step = not animate_step


py5.run_sketch()
