from __future__ import annotations

import math
from math import gcd
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    ("hypotrochoid bloom", "hypo", 160, 63, 96),
    ("epitrochoid crown", "epi", 116, 44, 82),
    ("hypotrochoid star", "hypo", 180, 72, 128),
    ("epitrochoid lace", "epi", 128, 36, 92),
    ("hypotrochoid knot", "hypo", 170, 51, 118),
]

preset_index = 0
draw_progress = 1.0
animate_trace = True
show_gear_guides = True
show_points = False


def setup() -> None:
    py5.size(760, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global draw_progress

    py5.background(218, 14, 96)
    name, mode, fixed_radius, rolling_radius, pen_distance = PRESETS[preset_index]
    points = trochoid_points(mode, fixed_radius, rolling_radius, pen_distance)

    if animate_trace:
        draw_progress += 0.008
        if draw_progress > 1.0:
            draw_progress = 0.0

    py5.translate(py5.width * 0.5, py5.height * 0.54)
    if show_gear_guides:
        draw_gear_guides(mode, fixed_radius, rolling_radius, pen_distance, draw_progress)
    draw_curve(points, draw_progress)
    if show_points:
        draw_sample_points(points)
    draw_moving_point(points, draw_progress)
    py5.reset_matrix()
    draw_info(name, mode, fixed_radius, rolling_radius, pen_distance, len(points))


def trochoid_points(
    mode: str, fixed_radius: float, rolling_radius: float, pen_distance: float
) -> list[tuple[float, float]]:
    cycle = rolling_radius / gcd(int(fixed_radius), int(rolling_radius))
    max_t = py5.TWO_PI * cycle
    steps = max(420, int(cycle * 260))
    points = []

    for i in range(steps + 1):
        t = max_t * i / steps
        if mode == "epi":
            x = (fixed_radius + rolling_radius) * math.cos(t) - pen_distance * math.cos(
                (fixed_radius + rolling_radius) * t / rolling_radius
            )
            y = (fixed_radius + rolling_radius) * math.sin(t) - pen_distance * math.sin(
                (fixed_radius + rolling_radius) * t / rolling_radius
            )
        else:
            x = (fixed_radius - rolling_radius) * math.cos(t) + pen_distance * math.cos(
                (fixed_radius - rolling_radius) * t / rolling_radius
            )
            y = (fixed_radius - rolling_radius) * math.sin(t) - pen_distance * math.sin(
                (fixed_radius - rolling_radius) * t / rolling_radius
            )
        points.append((x, y))

    return points


def draw_curve(points: list[tuple[float, float]], progress: float) -> None:
    visible_count = max(2, int(len(points) * progress))
    py5.no_fill()
    py5.stroke_weight(2.2)
    py5.begin_shape()
    for i, (x, y) in enumerate(points[:visible_count]):
        hue = (190 + i * 170 / max(1, len(points))) % 360
        py5.stroke(hue, 74, 48 + 42 * i / max(1, len(points)), 94)
        py5.vertex(x, y)
    py5.end_shape()


def draw_gear_guides(
    mode: str,
    fixed_radius: float,
    rolling_radius: float,
    pen_distance: float,
    progress: float,
) -> None:
    cycle = rolling_radius / gcd(int(fixed_radius), int(rolling_radius))
    t = py5.TWO_PI * cycle * progress
    sign = 1 if mode == "epi" else -1
    orbit_radius = fixed_radius + sign * rolling_radius
    rolling_x = orbit_radius * math.cos(t)
    rolling_y = orbit_radius * math.sin(t)

    if mode == "epi":
        pen_angle = (fixed_radius + rolling_radius) * t / rolling_radius
        pen_x = rolling_x - pen_distance * math.cos(pen_angle)
        pen_y = rolling_y - pen_distance * math.sin(pen_angle)
    else:
        pen_angle = (fixed_radius - rolling_radius) * t / rolling_radius
        pen_x = rolling_x + pen_distance * math.cos(pen_angle)
        pen_y = rolling_y - pen_distance * math.sin(pen_angle)

    py5.no_fill()
    py5.stroke(214, 30, 30, 26)
    py5.stroke_weight(1)
    py5.circle(0, 0, fixed_radius * 2)
    py5.circle(rolling_x, rolling_y, rolling_radius * 2)

    py5.stroke(30, 84, 46, 68)
    py5.stroke_weight(1.4)
    py5.line(rolling_x, rolling_y, pen_x, pen_y)


def draw_moving_point(points: list[tuple[float, float]], progress: float) -> None:
    index = min(len(points) - 1, max(0, int(len(points) * progress) - 1))
    x, y = points[index]
    py5.no_stroke()
    py5.fill(34, 94, 98, 100)
    py5.circle(x, y, 12)
    py5.fill(0, 0, 100, 100)
    py5.circle(x, y, 4)


def draw_sample_points(points: list[tuple[float, float]]) -> None:
    step = max(1, len(points) // 180)
    py5.no_stroke()
    for i in range(0, len(points), step):
        x, y = points[i]
        py5.fill((188 + i * 160 / len(points)) % 360, 66, 92, 74)
        py5.circle(x, y, 3.5)


def draw_info(
    name: str,
    mode: str,
    fixed_radius: float,
    rolling_radius: float,
    pen_distance: float,
    point_count: int,
) -> None:
    py5.no_stroke()
    py5.fill(218, 24, 12, 90)
    py5.rect(14, 14, 640, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Spirograph curves | {name} {mode} R={fixed_radius} r={rolling_radius} d={pen_distance} | points {point_count} | n: preset | space: animate | g: guides | p: points | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, draw_progress, animate_trace, show_gear_guides, show_points

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spirograph_curves_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        draw_progress = 1.0
    elif py5.key == " ":
        animate_trace = not animate_trace
    elif py5.key == "g":
        show_gear_guides = not show_gear_guides
    elif py5.key == "p":
        show_points = not show_points


py5.run_sketch()
