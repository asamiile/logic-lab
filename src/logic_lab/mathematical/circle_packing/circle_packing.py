from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass
class PackedCircle:
    x: float
    y: float
    radius: float
    hue: float
    growing: bool = True


circles: list[PackedCircle] = []
seed_value = 42
mask_mode = 0
show_fill = True
paused = False
max_circles = 420
growth_rate = 0.42


def setup() -> None:
    py5.size(700, 700)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_packing()


def draw() -> None:
    py5.background(214, 15, 96)
    if not paused:
        add_candidates(10)
        grow_circles()
    draw_mask_hint()
    draw_circles()
    draw_info()


def reset_packing() -> None:
    global circles

    random.seed(seed_value)
    circles = []


def add_candidates(count: int) -> None:
    if len(circles) >= max_circles:
        return

    attempts = 0
    added = 0
    while added < count and attempts < count * 80 and len(circles) < max_circles:
        attempts += 1
        point = random_point()
        if point is None:
            continue
        x, y = point
        if can_place_circle(x, y, 2.0):
            circles.append(PackedCircle(x, y, 2.0, hue_for_point(x, y)))
            added += 1


def random_point() -> tuple[float, float] | None:
    margin = 34
    x = random.uniform(margin, py5.width - margin)
    y = random.uniform(margin, py5.height - margin)
    if inside_mask(x, y):
        return x, y
    return None


def inside_mask(x: float, y: float) -> bool:
    cx = py5.width * 0.5
    cy = py5.height * 0.5
    dx = x - cx
    dy = y - cy

    if mask_mode == 1:
        radius = min(py5.width, py5.height) * 0.42
        return dx * dx + dy * dy <= radius * radius
    if mask_mode == 2:
        angle = math.atan2(dy, dx)
        radius = min(py5.width, py5.height) * (0.26 + 0.13 * math.cos(5 * angle))
        return math.hypot(dx, dy) <= radius
    return True


def can_place_circle(x: float, y: float, radius: float) -> bool:
    if not inside_mask(x, y):
        return False
    for circle in circles:
        distance = math.hypot(x - circle.x, y - circle.y)
        if distance < radius + circle.radius + 2:
            return False
    return True


def grow_circles() -> None:
    for circle in circles:
        if not circle.growing:
            continue
        if touches_boundary(circle) or touches_neighbor(circle):
            circle.growing = False
        else:
            circle.radius += growth_rate


def touches_boundary(circle: PackedCircle) -> bool:
    next_radius = circle.radius + growth_rate + 1.5
    sample_count = 16
    for i in range(sample_count):
        angle = py5.TWO_PI * i / sample_count
        x = circle.x + math.cos(angle) * next_radius
        y = circle.y + math.sin(angle) * next_radius
        if not inside_mask(x, y):
            return True
        if x < 12 or x > py5.width - 12 or y < 12 or y > py5.height - 12:
            return True
    return False


def touches_neighbor(circle: PackedCircle) -> bool:
    for other in circles:
        if other is circle:
            continue
        distance = math.hypot(circle.x - other.x, circle.y - other.y)
        if distance <= circle.radius + other.radius + growth_rate + 1.0:
            return True
    return False


def hue_for_point(x: float, y: float) -> float:
    angle = math.atan2(y - py5.height * 0.5, x - py5.width * 0.5)
    radius = math.hypot(x - py5.width * 0.5, y - py5.height * 0.5)
    return (38 + math.degrees(angle) * 0.45 + radius * 0.08) % 360


def draw_mask_hint() -> None:
    if mask_mode == 0:
        return
    py5.no_fill()
    py5.stroke(210, 24, 36, 18)
    py5.stroke_weight(1)
    py5.begin_shape()
    cx = py5.width * 0.5
    cy = py5.height * 0.5
    for i in range(180):
        angle = py5.TWO_PI * i / 180
        if mask_mode == 1:
            radius = min(py5.width, py5.height) * 0.42
        else:
            radius = min(py5.width, py5.height) * (0.26 + 0.13 * math.cos(5 * angle))
        py5.vertex(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
    py5.end_shape(py5.CLOSE)


def draw_circles() -> None:
    for circle in sorted(circles, key=lambda item: item.radius, reverse=True):
        if show_fill:
            py5.fill(circle.hue, 56, 92, 70)
        else:
            py5.no_fill()
        py5.stroke((circle.hue + 20) % 360, 72, 38, 82)
        py5.stroke_weight(1.2)
        py5.circle(circle.x, circle.y, circle.radius * 2)
        if circle.growing:
            py5.no_stroke()
            py5.fill(42, 94, 98, 92)
            py5.circle(circle.x, circle.y, 3.5)


def draw_info() -> None:
    growing_count = sum(1 for circle in circles if circle.growing)
    mask_name = ["rectangle", "circle", "flower"][mask_mode]
    py5.no_stroke()
    py5.fill(214, 24, 12, 90)
    py5.rect(14, 14, 590, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Circle packing | {mask_name} | circles {len(circles)} | growing {growing_count} | r: reset | m: mask | f: fill | space: pause | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global seed_value, mask_mode, show_fill, paused

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "circle_packing_####.png"))
    elif py5.key == "r":
        seed_value = random.randint(0, 100000)
        reset_packing()
    elif py5.key == "m":
        mask_mode = (mask_mode + 1) % 3
        reset_packing()
    elif py5.key == "f":
        show_fill = not show_fill
    elif py5.key == " ":
        paused = not paused


py5.run_sketch()
