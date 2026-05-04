from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

order = 5
draw_progress = 1.0
animate_curve = True
show_points = False
show_grid = False


def setup() -> None:
    py5.size(720, 720)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global draw_progress

    py5.background(216, 14, 96)
    points = hilbert_points(order)

    if animate_curve:
        draw_progress += 0.006
        if draw_progress > 1.0:
            draw_progress = 0.0

    if show_grid:
        draw_grid(order)
    draw_curve(points, draw_progress)
    if show_points:
        draw_sample_points(points, draw_progress)
    draw_info(len(points))


def hilbert_points(curve_order: int) -> list[tuple[float, float]]:
    grid_size = 2**curve_order
    count = grid_size * grid_size
    margin = 72
    cell = (py5.width - margin * 2) / max(1, grid_size - 1)
    points = []

    for index in range(count):
        x, y = hilbert_index_to_xy(index, grid_size)
        points.append((margin + x * cell, margin + y * cell))

    return points


def hilbert_index_to_xy(index: int, grid_size: int) -> tuple[int, int]:
    x = 0
    y = 0
    t = index
    scale = 1

    while scale < grid_size:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        x, y = rotate_quadrant(scale, x, y, rx, ry)
        x += scale * rx
        y += scale * ry
        t //= 4
        scale *= 2

    return x, y


def rotate_quadrant(scale: int, x: int, y: int, rx: int, ry: int) -> tuple[int, int]:
    if ry == 0:
        if rx == 1:
            x = scale - 1 - x
            y = scale - 1 - y
        x, y = y, x
    return x, y


def draw_grid(curve_order: int) -> None:
    grid_size = 2**curve_order
    margin = 72
    cell = (py5.width - margin * 2) / max(1, grid_size - 1)

    py5.stroke(220, 16, 36, 18)
    py5.stroke_weight(1)
    for i in range(grid_size):
        coord = margin + i * cell
        py5.line(margin, coord, py5.width - margin, coord)
        py5.line(coord, margin, coord, py5.height - margin)


def draw_curve(points: list[tuple[float, float]], progress: float) -> None:
    visible_count = max(2, int(len(points) * progress))
    visible = points[:visible_count]

    py5.no_fill()
    py5.stroke_weight(max(1.2, 6.4 - order * 0.8))
    py5.begin_shape()
    for i, (x, y) in enumerate(visible):
        hue = (190 + i * 180 / max(1, len(points))) % 360
        py5.stroke(hue, 76, 42 + 42 * i / max(1, len(points)), 94)
        py5.vertex(x, y)
    py5.end_shape()

    if visible:
        x, y = visible[-1]
        py5.no_stroke()
        py5.fill(38, 94, 98, 100)
        py5.circle(x, y, 10)


def draw_sample_points(points: list[tuple[float, float]], progress: float) -> None:
    visible_count = max(2, int(len(points) * progress))
    step = max(1, len(points) // 256)
    py5.no_stroke()
    for i in range(0, visible_count, step):
        x, y = points[i]
        py5.fill((190 + i * 180 / len(points)) % 360, 72, 92, 82)
        py5.circle(x, y, max(2.2, 7.4 - order))


def draw_info(point_count: int) -> None:
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 610, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Hilbert curve | order {order} | points {point_count} | +/-: order | space: animate | p: points | g: grid | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global order, draw_progress, animate_curve, show_points, show_grid

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hilbert_curve_####.png"))
    elif py5.key == "+":
        order = min(7, order + 1)
        draw_progress = 1.0
    elif py5.key == "-":
        order = max(1, order - 1)
        draw_progress = 1.0
    elif py5.key == " ":
        animate_curve = not animate_curve
    elif py5.key == "p":
        show_points = not show_points
    elif py5.key == "g":
        show_grid = not show_grid


py5.run_sketch()
