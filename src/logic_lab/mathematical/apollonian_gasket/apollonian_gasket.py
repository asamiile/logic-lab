from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Circle:
    x: float
    y: float
    radius: float
    curvature: float


circles: list[Circle] = []
min_radius = 3.6
show_fill = True
show_curvature = False
max_circles = 900


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    generate_gasket()


def draw() -> None:
    py5.background(216, 14, 96)
    draw_circles()
    draw_info()


def generate_gasket() -> None:
    global circles

    outer_radius = 300.0
    center_x = py5.width * 0.5
    center_y = py5.height * 0.52
    inner_radius = math.sqrt(3) * outer_radius / (2 + math.sqrt(3))
    orbit_radius = outer_radius - inner_radius

    outer = Circle(center_x, center_y, outer_radius, -1.0 / outer_radius)
    inner = []
    for i in range(3):
        angle = -py5.HALF_PI + py5.TWO_PI * i / 3
        inner.append(
            Circle(
                center_x + math.cos(angle) * orbit_radius,
                center_y + math.sin(angle) * orbit_radius,
                inner_radius,
                1.0 / inner_radius,
            )
        )

    circles = [outer] + inner
    seen = {circle_key(circle) for circle in circles}
    queue = [
        (0, 1, 2, 3),
    ]

    while queue and len(circles) < max_circles:
        quad = queue.pop(0)
        for replace_index in range(4):
            next_circle = reflect_circle(quad, replace_index, circles)
            if next_circle is None or next_circle.radius < min_radius:
                continue
            key = circle_key(next_circle)
            if key in seen:
                continue
            if not inside_outer(next_circle, outer):
                continue
            seen.add(key)
            circles.append(next_circle)
            new_index = len(circles) - 1
            next_quad = list(quad)
            next_quad[replace_index] = new_index
            queue.append(tuple(next_quad))


def reflect_circle(quad: tuple[int, int, int, int], replace_index: int, all_circles: list[Circle]) -> Circle | None:
    old = all_circles[quad[replace_index]]
    others = [all_circles[quad[i]] for i in range(4) if i != replace_index]

    sum_curvature = sum(circle.curvature for circle in others)
    new_curvature = 2 * sum_curvature - old.curvature
    if abs(new_curvature) < 1e-9:
        return None

    old_bz = old.curvature * complex(old.x, old.y)
    sum_bz = sum(circle.curvature * complex(circle.x, circle.y) for circle in others)
    new_center = (2 * sum_bz - old_bz) / new_curvature
    new_radius = abs(1.0 / new_curvature)
    return Circle(new_center.real, new_center.imag, new_radius, new_curvature)


def inside_outer(circle: Circle, outer: Circle) -> bool:
    if circle.curvature < 0:
        return False
    distance = math.hypot(circle.x - outer.x, circle.y - outer.y)
    return distance + circle.radius <= outer.radius + 0.5


def circle_key(circle: Circle) -> tuple[int, int, int]:
    return (round(circle.x * 10), round(circle.y * 10), round(circle.radius * 10))


def draw_circles() -> None:
    drawable = [circle for circle in circles if circle.curvature > 0]
    drawable.sort(key=lambda circle: circle.radius, reverse=True)

    for circle in drawable:
        hue = (198 + circle.radius * 0.7 + abs(circle.curvature) * 900) % 360
        if show_fill:
            py5.fill(hue, 52, 92, 42 + min(42, circle.radius * 0.18))
        else:
            py5.no_fill()
        py5.stroke((hue + 22) % 360, 72, 42, 82)
        py5.stroke_weight(max(0.55, min(2.2, circle.radius * 0.028)))
        py5.circle(circle.x, circle.y, circle.radius * 2)

        if show_curvature and circle.radius > 18:
            py5.no_stroke()
            py5.fill(220, 24, 14, 76)
            py5.text(f"{circle.curvature:.3f}", circle.x - 12, circle.y + 4)

    outer = circles[0]
    py5.no_fill()
    py5.stroke(220, 28, 24, 70)
    py5.stroke_weight(2.2)
    py5.circle(outer.x, outer.y, outer.radius * 2)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 590, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Apollonian gasket | circles {len(circles) - 1} | min radius {min_radius:.1f} | +/-: detail | f: fill | k: curvature | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global min_radius, show_fill, show_curvature

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "apollonian_gasket_####.png"))
    elif py5.key == "+":
        min_radius = max(1.4, min_radius - 0.6)
        generate_gasket()
    elif py5.key == "-":
        min_radius = min(18.0, min_radius + 0.6)
        generate_gasket()
    elif py5.key == "f":
        show_fill = not show_fill
    elif py5.key == "k":
        show_curvature = not show_curvature


py5.run_sketch()
