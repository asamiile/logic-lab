from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]

vertices: list[Point] = []
selected_index: int | None = None
show_grid = True
show_weights = True


def setup() -> None:
    py5.size(720, 640)
    py5.color_mode(py5.RGB, 255, 255, 255, 255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_vertices()


def draw() -> None:
    py5.background(245, 246, 242)
    draw_weight_field()
    if show_grid:
        draw_weight_grid()
    draw_triangle()
    if show_weights:
        draw_mouse_weights()
    draw_info()


def reset_vertices() -> None:
    global vertices, selected_index

    vertices = [
        (py5.width * 0.50, 90),
        (120, py5.height - 105),
        (py5.width - 115, py5.height - 120),
    ]
    selected_index = None


def barycentric(point: Point, triangle: list[Point]) -> tuple[float, float, float]:
    px, py = point
    ax, ay = triangle[0]
    bx, by = triangle[1]
    cx, cy = triangle[2]

    denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(denom) < 1e-9:
        return 0.0, 0.0, 0.0

    w1 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / denom
    w2 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / denom
    w3 = 1.0 - w1 - w2
    return w1, w2, w3


def inside_triangle(weights: tuple[float, float, float]) -> bool:
    return all(weight >= -1e-5 for weight in weights)


def draw_weight_field() -> None:
    step = 4
    py5.no_stroke()
    for y in range(0, py5.height, step):
        for x in range(0, py5.width, step):
            weights = barycentric((x + step * 0.5, y + step * 0.5), vertices)
            if not inside_triangle(weights):
                continue
            r = max(0, min(255, int(weights[0] * 255)))
            g = max(0, min(255, int(weights[1] * 255)))
            b = max(0, min(255, int(weights[2] * 255)))
            py5.fill(r, g, b, 214)
            py5.rect(x, y, step + 1, step + 1)


def draw_weight_grid() -> None:
    py5.no_fill()
    for level in [0.2, 0.4, 0.6, 0.8]:
        draw_weight_level(0, level, (225, 70, 72, 105))
        draw_weight_level(1, level, (60, 150, 82, 105))
        draw_weight_level(2, level, (70, 100, 230, 105))


def draw_weight_level(weight_index: int, level: float, color: tuple[int, int, int, int]) -> None:
    py5.stroke(*color)
    py5.stroke_weight(1.2)
    points = []
    samples = 90
    for i in range(samples + 1):
        t = i / samples
        weights = [0.0, 0.0, 0.0]
        weights[weight_index] = level
        other = [idx for idx in range(3) if idx != weight_index]
        weights[other[0]] = (1 - level) * t
        weights[other[1]] = (1 - level) * (1 - t)
        points.append(from_barycentric(tuple(weights), vertices))

    py5.begin_shape()
    for x, y in points:
        py5.vertex(x, y)
    py5.end_shape()


def from_barycentric(weights: tuple[float, float, float], triangle: list[Point]) -> Point:
    x = sum(weights[i] * triangle[i][0] for i in range(3))
    y = sum(weights[i] * triangle[i][1] for i in range(3))
    return x, y


def draw_triangle() -> None:
    py5.no_fill()
    py5.stroke(30, 34, 34, 220)
    py5.stroke_weight(2.5)
    py5.triangle(
        vertices[0][0],
        vertices[0][1],
        vertices[1][0],
        vertices[1][1],
        vertices[2][0],
        vertices[2][1],
    )

    colors = [(235, 52, 62), (42, 170, 88), (55, 94, 230)]
    py5.no_stroke()
    for i, (x, y) in enumerate(vertices):
        py5.fill(30, 34, 34, 160)
        py5.circle(x, y, 19)
        py5.fill(*colors[i], 255)
        py5.circle(x, y, 12)
        py5.fill(30, 34, 34, 230)
        py5.text(f"v{i}", x + 12, y - 10)


def draw_mouse_weights() -> None:
    weights = barycentric((py5.mouse_x, py5.mouse_y), vertices)
    point = from_barycentric(weights, vertices)
    py5.stroke(30, 34, 34, 110)
    py5.stroke_weight(1)
    for vx, vy in vertices:
        py5.line(py5.mouse_x, py5.mouse_y, vx, vy)

    py5.no_stroke()
    if inside_triangle(weights):
        py5.fill(255, 255, 255, 230)
        py5.circle(point[0], point[1], 16)
        py5.fill(30, 34, 34, 255)
        py5.circle(point[0], point[1], 6)

    py5.fill(30, 34, 34, 230)
    py5.rect(14, py5.height - 58, 365, 42, 4)
    py5.fill(255, 255, 255, 255)
    py5.text(
        f"mouse weights: ({weights[0]:.2f}, {weights[1]:.2f}, {weights[2]:.2f})",
        24,
        py5.height - 32,
    )


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(30, 34, 34, 230)
    py5.rect(14, 14, 570, 54, 4)
    py5.fill(255, 255, 255, 255)
    py5.text(
        "Barycentric coordinates | drag vertices | g: grid | w: weights | r: reset | s: save",
        24,
        46,
    )


def mouse_pressed() -> None:
    global selected_index

    selected_index = None
    for i, (x, y) in enumerate(vertices):
        if py5.dist(py5.mouse_x, py5.mouse_y, x, y) < 22:
            selected_index = i
            break


def mouse_dragged() -> None:
    if selected_index is not None:
        vertices[selected_index] = (py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    global selected_index
    selected_index = None


def key_pressed() -> None:
    global show_grid, show_weights

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "barycentric_coordinates_####.png"))
    elif py5.key == "g":
        show_grid = not show_grid
    elif py5.key == "w":
        show_weights = not show_weights
    elif py5.key == "r":
        reset_vertices()


py5.run_sketch()
