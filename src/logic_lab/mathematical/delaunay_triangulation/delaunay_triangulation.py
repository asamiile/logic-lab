from __future__ import annotations

import math
import random
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]
Triangle = tuple[int, int, int]

points: list[Point] = []
triangles: list[Triangle] = []
show_circles = False
show_fill = True
point_count = 42
seed_value = 12


def setup() -> None:
    py5.size(700, 700)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    regenerate_points()


def draw() -> None:
    py5.background(214, 16, 96)
    draw_triangles()
    if show_circles:
        draw_circumcircles()
    draw_points()
    draw_info()


def regenerate_points() -> None:
    global points, triangles, seed_value

    random.seed(seed_value)
    margin = 72
    points = [
        (
            random.uniform(margin, py5.width - margin),
            random.uniform(margin, py5.height - margin),
        )
        for _ in range(point_count)
    ]
    triangles = bowyer_watson(points)


def bowyer_watson(input_points: list[Point]) -> list[Triangle]:
    working_points = list(input_points)
    super_triangle = make_super_triangle(input_points)
    super_start = len(working_points)
    working_points.extend(super_triangle)

    result: list[Triangle] = [(super_start, super_start + 1, super_start + 2)]

    for point_index, point in enumerate(input_points):
        bad_triangles = [
            triangle
            for triangle in result
            if point_in_circumcircle(point, triangle, working_points)
        ]

        polygon = boundary_edges(bad_triangles)
        result = [triangle for triangle in result if triangle not in bad_triangles]

        for edge in polygon:
            candidate = orient_triangle((edge[0], edge[1], point_index), working_points)
            result.append(candidate)

    return [triangle for triangle in result if all(vertex < super_start for vertex in triangle)]


def make_super_triangle(input_points: list[Point]) -> list[Point]:
    min_x = min(point[0] for point in input_points)
    max_x = max(point[0] for point in input_points)
    min_y = min(point[1] for point in input_points)
    max_y = max(point[1] for point in input_points)
    delta = max(max_x - min_x, max_y - min_y)
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    radius = delta * 8
    return [
        (center_x, center_y - radius),
        (center_x - radius, center_y + radius),
        (center_x + radius, center_y + radius),
    ]


def point_in_circumcircle(point: Point, triangle: Triangle, all_points: list[Point]) -> bool:
    circle = circumcircle(triangle, all_points)
    if circle is None:
        return False
    cx, cy, radius_sq = circle
    dx = point[0] - cx
    dy = point[1] - cy
    return dx * dx + dy * dy <= radius_sq + 1e-6


def circumcircle(triangle: Triangle, all_points: list[Point]) -> tuple[float, float, float] | None:
    ax, ay = all_points[triangle[0]]
    bx, by = all_points[triangle[1]]
    cx, cy = all_points[triangle[2]]

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        return None

    ax_sq = ax * ax + ay * ay
    bx_sq = bx * bx + by * by
    cx_sq = cx * cx + cy * cy
    ux = (ax_sq * (by - cy) + bx_sq * (cy - ay) + cx_sq * (ay - by)) / d
    uy = (ax_sq * (cx - bx) + bx_sq * (ax - cx) + cx_sq * (bx - ax)) / d
    dx = ux - ax
    dy = uy - ay
    return ux, uy, dx * dx + dy * dy


def boundary_edges(bad_triangles: list[Triangle]) -> list[tuple[int, int]]:
    edge_counts: dict[tuple[int, int], int] = {}
    oriented_edges: dict[tuple[int, int], tuple[int, int]] = {}

    for a, b, c in bad_triangles:
        for edge in ((a, b), (b, c), (c, a)):
            key = tuple(sorted(edge))
            edge_counts[key] = edge_counts.get(key, 0) + 1
            oriented_edges[key] = edge

    return [oriented_edges[key] for key, count in edge_counts.items() if count == 1]


def orient_triangle(triangle: Triangle, all_points: list[Point]) -> Triangle:
    a, b, c = triangle
    ax, ay = all_points[a]
    bx, by = all_points[b]
    cx, cy = all_points[c]
    cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if cross < 0:
        return (a, c, b)
    return triangle


def draw_triangles() -> None:
    if show_fill:
        py5.stroke(210, 42, 24, 46)
        py5.stroke_weight(1)
    else:
        py5.no_fill()
        py5.stroke(210, 60, 24, 82)
        py5.stroke_weight(1.4)

    for i, triangle in enumerate(triangles):
        a, b, c = (points[index] for index in triangle)
        if show_fill:
            hue = (188 + i * 5) % 360
            area = triangle_area(a, b, c)
            py5.fill(hue, 46, 88 - min(36, area * 0.0006), 62)
        py5.triangle(a[0], a[1], b[0], b[1], c[0], c[1])


def draw_circumcircles() -> None:
    py5.no_fill()
    py5.stroke(24, 78, 72, 28)
    py5.stroke_weight(1)
    for triangle in triangles:
        circle = circumcircle(triangle, points)
        if circle is None:
            continue
        cx, cy, radius_sq = circle
        py5.circle(cx, cy, math.sqrt(radius_sq) * 2)


def draw_points() -> None:
    py5.no_stroke()
    for x, y in points:
        py5.fill(212, 70, 12, 86)
        py5.circle(x, y, 9)
        py5.fill(42, 88, 98, 100)
        py5.circle(x, y, 4.5)


def triangle_area(a: Point, b: Point, c: Point) -> float:
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) * 0.5


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(214, 24, 12, 90)
    py5.rect(14, 14, 535, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Delaunay triangulation | points {len(points)} | triangles {len(triangles)} | click: add | r: random | +/-: count | f: fill | c: circles | s: save",
        24,
        46,
    )


def mouse_pressed() -> None:
    global points, triangles

    if 0 <= py5.mouse_x < py5.width and 0 <= py5.mouse_y < py5.height:
        points.append((py5.mouse_x, py5.mouse_y))
        triangles = bowyer_watson(points)


def key_pressed() -> None:
    global point_count, seed_value, triangles, show_circles, show_fill

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "delaunay_triangulation_####.png"))
    elif py5.key == "r":
        seed_value = random.randint(0, 100000)
        regenerate_points()
    elif py5.key == "+":
        point_count = min(180, point_count + 4)
        regenerate_points()
    elif py5.key == "-":
        point_count = max(6, point_count - 4)
        regenerate_points()
    elif py5.key == "c":
        show_circles = not show_circles
    elif py5.key == "f":
        show_fill = not show_fill


py5.run_sketch()
