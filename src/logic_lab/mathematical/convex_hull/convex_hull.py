from __future__ import annotations

import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]

points: list[Point] = []
hull: list[Point] = []
point_count = 64
seed_value = 19
show_fill = True
show_sorted_path = False


def setup() -> None:
    py5.size(700, 700)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    regenerate_points()


def draw() -> None:
    py5.background(212, 14, 96)
    if show_sorted_path:
        draw_sorted_path()
    draw_hull()
    draw_points()
    draw_info()


def regenerate_points() -> None:
    global points, hull, seed_value

    random.seed(seed_value)
    margin = 72
    center_x = py5.width * 0.5
    center_y = py5.height * 0.5
    points = []
    for _ in range(point_count):
        # A slight radial bias keeps the hull visually varied while preserving randomness.
        radius = random.random() ** 0.72
        angle = random.uniform(0, py5.TWO_PI)
        spread_x = (py5.width * 0.5 - margin) * radius
        spread_y = (py5.height * 0.5 - margin) * radius
        points.append(
            (
                center_x + py5.cos(angle) * spread_x,
                center_y + py5.sin(angle) * spread_y,
            )
        )
    hull = convex_hull(points)


def convex_hull(input_points: list[Point]) -> list[Point]:
    ordered = sorted(set(input_points))
    if len(ordered) <= 1:
        return ordered

    lower: list[Point] = []
    for point in ordered:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[Point] = []
    for point in reversed(ordered):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def cross(origin: Point, a: Point, b: Point) -> float:
    return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])


def draw_sorted_path() -> None:
    ordered = sorted(points)
    if len(ordered) < 2:
        return

    py5.no_fill()
    py5.stroke(210, 30, 44, 22)
    py5.stroke_weight(1)
    py5.begin_shape()
    for x, y in ordered:
        py5.vertex(x, y)
    py5.end_shape()


def draw_hull() -> None:
    if len(hull) < 3:
        return

    if show_fill:
        py5.fill(38, 62, 98, 26)
    else:
        py5.no_fill()
    py5.stroke(30, 82, 48, 95)
    py5.stroke_weight(3)
    py5.begin_shape()
    for x, y in hull:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)

    py5.stroke(30, 86, 96, 90)
    py5.stroke_weight(1.4)
    py5.no_fill()
    py5.begin_shape()
    for x, y in hull:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)


def draw_points() -> None:
    hull_set = set(hull)
    py5.no_stroke()
    for x, y in points:
        if (x, y) in hull_set:
            py5.fill(24, 92, 96, 100)
            py5.circle(x, y, 10)
            py5.fill(0, 0, 100, 100)
            py5.circle(x, y, 4)
        else:
            py5.fill(210, 56, 24, 66)
            py5.circle(x, y, 5)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(212, 24, 12, 90)
    py5.rect(14, 14, 570, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Convex hull | points {len(points)} | hull vertices {len(hull)} | click: add | r: random | +/-: count | f: fill | o: sorted path | s: save",
        24,
        46,
    )


def mouse_pressed() -> None:
    global hull

    if 0 <= py5.mouse_x < py5.width and 0 <= py5.mouse_y < py5.height:
        points.append((py5.mouse_x, py5.mouse_y))
        hull = convex_hull(points)


def key_pressed() -> None:
    global point_count, seed_value, show_fill, show_sorted_path

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "convex_hull_####.png"))
    elif py5.key == "r":
        seed_value = random.randint(0, 100000)
        regenerate_points()
    elif py5.key == "+":
        point_count = min(240, point_count + 8)
        regenerate_points()
    elif py5.key == "-":
        point_count = max(3, point_count - 8)
        regenerate_points()
    elif py5.key == "f":
        show_fill = not show_fill
    elif py5.key == "o":
        show_sorted_path = not show_sorted_path


py5.run_sketch()
