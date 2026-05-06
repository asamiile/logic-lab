from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    (
        "pendulum bloom",
        (2.01, 3.00, 1.98, 3.01),
        (0.010, 0.012, 0.011, 0.013),
        (0.0, 1.4, 0.8, 2.1),
    ),
    ("lace decay", (3.00, 2.00, 3.05, 2.02), (0.006, 0.009, 0.007, 0.010), (0.2, 1.7, 1.1, 2.8)),
    ("orbital knot", (2.92, 4.03, 3.01, 1.99), (0.008, 0.011, 0.009, 0.012), (1.0, 0.4, 2.2, 1.5)),
    ("woven fan", (4.01, 3.00, 2.00, 5.02), (0.012, 0.010, 0.008, 0.013), (0.3, 2.0, 1.3, 2.7)),
]

preset_index = 0
sample_count = 5200
draw_progress = 1.0
animate_trace = True
show_points = False


def setup() -> None:
    py5.size(760, 760)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global draw_progress

    py5.background(220, 14, 96)
    if animate_trace:
        draw_progress += 0.006
        if draw_progress > 1.0:
            draw_progress = 0.0

    points = harmonograph_points()
    py5.translate(py5.width * 0.5, py5.height * 0.52)
    draw_curve(points, draw_progress)
    if show_points:
        draw_sample_points(points, draw_progress)
    py5.reset_matrix()
    draw_info(len(points))


def harmonograph_points() -> list[tuple[float, float]]:
    _, frequencies, damping, phases = PRESETS[preset_index]
    scale = min(py5.width, py5.height) * 0.22
    points = []

    for i in range(sample_count):
        t = i * 0.012
        x = math.sin(frequencies[0] * t + phases[0]) * math.exp(-damping[0] * t) + math.sin(
            frequencies[1] * t + phases[1]
        ) * math.exp(-damping[1] * t)
        y = math.sin(frequencies[2] * t + phases[2]) * math.exp(-damping[2] * t) + math.sin(
            frequencies[3] * t + phases[3]
        ) * math.exp(-damping[3] * t)
        points.append((x * scale, y * scale))

    return points


def draw_curve(points: list[tuple[float, float]], progress: float) -> None:
    visible_count = max(2, int(len(points) * progress))
    visible = points[:visible_count]

    py5.no_fill()
    py5.stroke_weight(1.2)
    py5.begin_shape()
    for i, (x, y) in enumerate(visible):
        hue = (194 + i * 170 / max(1, len(points))) % 360
        brightness = 28 + 68 * i / max(1, len(points))
        py5.stroke(hue, 74, brightness, 78)
        py5.vertex(x, y)
    py5.end_shape()

    if visible:
        x, y = visible[-1]
        py5.no_stroke()
        py5.fill(36, 94, 98, 100)
        py5.circle(x, y, 10)


def draw_sample_points(points: list[tuple[float, float]], progress: float) -> None:
    visible_count = max(2, int(len(points) * progress))
    step = max(1, len(points) // 220)
    py5.no_stroke()
    for i in range(0, visible_count, step):
        x, y = points[i]
        py5.fill((190 + i * 140 / len(points)) % 360, 72, 92, 72)
        py5.circle(x, y, 3.2)


def draw_info(point_count: int) -> None:
    name, frequencies, damping, _ = PRESETS[preset_index]
    py5.no_stroke()
    py5.fill(220, 24, 12, 90)
    py5.rect(14, 14, 650, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Harmonograph | {name} | freq {frequencies[0]:.2f},{frequencies[1]:.2f},{frequencies[2]:.2f},{frequencies[3]:.2f} | samples {point_count} | n: preset | +/-: samples | p: points | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, sample_count, draw_progress, animate_trace, show_points

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "harmonograph_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        draw_progress = 1.0
    elif py5.key == "+":
        sample_count = min(12000, sample_count + 600)
    elif py5.key == "-":
        sample_count = max(1000, sample_count - 600)
    elif py5.key == "p":
        show_points = not show_points
    elif py5.key == " ":
        animate_trace = not animate_trace


py5.run_sketch()
