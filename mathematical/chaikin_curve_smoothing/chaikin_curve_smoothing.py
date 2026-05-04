from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]

control_points: list[Point] = []
iteration_count = 4
closed_curve = True
show_polygon = True
show_levels = True
selected_index: int | None = None


def setup() -> None:
    py5.size(720, 640)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_points()


def draw() -> None:
    py5.background(216, 14, 96)
    levels = chaikin_levels(control_points, iteration_count, closed_curve)
    if show_levels:
        draw_intermediate_levels(levels)
    draw_smoothed_curve(levels[-1])
    if show_polygon:
        draw_control_polygon()
    draw_info(len(levels[-1]))


def reset_points() -> None:
    global control_points, selected_index

    control_points = [
        (118, 500),
        (170, 150),
        (310, 250),
        (420, 105),
        (598, 240),
        (545, 520),
        (342, 455),
    ]
    selected_index = None


def chaikin_levels(points: list[Point], iterations: int, closed: bool) -> list[list[Point]]:
    levels = [points]
    current = points
    for _ in range(iterations):
        current = chaikin_once(current, closed)
        levels.append(current)
    return levels


def chaikin_once(points: list[Point], closed: bool) -> list[Point]:
    if len(points) < 2:
        return points

    next_points: list[Point] = []
    if not closed:
        next_points.append(points[0])

    edge_count = len(points) if closed else len(points) - 1
    for i in range(edge_count):
        p0 = points[i]
        p1 = points[(i + 1) % len(points)]
        q = interpolate(p0, p1, 0.25)
        r = interpolate(p0, p1, 0.75)
        next_points.extend([q, r])

    if not closed:
        next_points.append(points[-1])

    return next_points


def interpolate(a: Point, b: Point, amount: float) -> Point:
    return (a[0] + (b[0] - a[0]) * amount, a[1] + (b[1] - a[1]) * amount)


def draw_intermediate_levels(levels: list[list[Point]]) -> None:
    for level_index, points in enumerate(levels[1:-1], start=1):
        hue = (198 + level_index * 22) % 360
        py5.no_fill()
        py5.stroke(hue, 36, 48, 22 + level_index * 8)
        py5.stroke_weight(1)
        draw_polyline(points, closed_curve)


def draw_smoothed_curve(points: list[Point]) -> None:
    py5.no_fill()
    py5.stroke(34, 88, 96, 96)
    py5.stroke_weight(3)
    draw_polyline(points, closed_curve)

    py5.stroke(202, 74, 42, 28)
    py5.stroke_weight(8)
    draw_polyline(points, closed_curve)


def draw_control_polygon() -> None:
    py5.no_fill()
    py5.stroke(220, 28, 24, 62)
    py5.stroke_weight(1.6)
    draw_polyline(control_points, closed_curve)

    py5.no_stroke()
    for i, (x, y) in enumerate(control_points):
        py5.fill(220, 68, 14, 82)
        py5.circle(x, y, 17)
        py5.fill(42, 94, 98, 100)
        py5.circle(x, y, 8)
        py5.fill(220, 24, 18, 88)
        py5.text(str(i), x + 11, y - 10)


def draw_polyline(points: list[Point], closed: bool) -> None:
    py5.begin_shape()
    for x, y in points:
        py5.vertex(x, y)
    if closed:
        py5.end_shape(py5.CLOSE)
    else:
        py5.end_shape()


def draw_info(point_count: int) -> None:
    mode = "closed" if closed_curve else "open"
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 630, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Chaikin curve smoothing | {mode} | iterations {iteration_count} | points {point_count} | drag points | +/-: iterations | c: closed | p: polygon | l: levels | r: reset | s: save",
        24,
        46,
    )


def mouse_pressed() -> None:
    global selected_index

    selected_index = None
    for i, (x, y) in enumerate(control_points):
        if py5.dist(py5.mouse_x, py5.mouse_y, x, y) < 22:
            selected_index = i
            break


def mouse_dragged() -> None:
    if selected_index is not None:
        control_points[selected_index] = (py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    global selected_index
    selected_index = None


def key_pressed() -> None:
    global iteration_count, closed_curve, show_polygon, show_levels

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "chaikin_curve_smoothing_####.png"))
    elif py5.key == "+":
        iteration_count = min(8, iteration_count + 1)
    elif py5.key == "-":
        iteration_count = max(0, iteration_count - 1)
    elif py5.key == "c":
        closed_curve = not closed_curve
    elif py5.key == "p":
        show_polygon = not show_polygon
    elif py5.key == "l":
        show_levels = not show_levels
    elif py5.key == "r":
        reset_points()


py5.run_sketch()
