from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 3

operation_mode = 0
show_contours = True
animate_shapes = True
field_pixels: np.ndarray | None = None


def setup() -> None:
    py5.size(690, 690)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global field_pixels

    t = py5.frame_count * 0.018 if animate_shapes else 0.0
    distances = compute_distance_field(t)
    draw_distance_field(distances)
    if show_contours:
        draw_contour_lines(distances)
    draw_info()


def compute_distance_field(t: float) -> np.ndarray:
    cols = py5.width // PIXEL_STEP
    rows = py5.height // PIXEL_STEP
    distances = np.zeros((rows, cols), dtype=np.float32)

    for row in range(rows):
        y = row * PIXEL_STEP - py5.height * 0.5
        for col in range(cols):
            x = col * PIXEL_STEP - py5.width * 0.5
            distances[row, col] = scene_sdf(x, y, t)

    return distances


def scene_sdf(x: float, y: float, t: float) -> float:
    circle_x = math.cos(t * 1.2) * 72
    circle_y = math.sin(t * 0.9) * 58
    d_circle = circle_sdf(x - circle_x, y - circle_y, 128)

    angle = t * 0.55
    rx, ry = rotate_point(x + 78, y - 26, angle)
    d_box = box_sdf(rx, ry, 116, 82)

    rx2, ry2 = rotate_point(x - 82, y + 72, -angle * 0.8)
    d_round_box = rounded_box_sdf(rx2, ry2, 96, 62, 24)

    if operation_mode == 1:
        return sdf_intersection(d_circle, d_box)
    if operation_mode == 2:
        return sdf_subtraction(sdf_union(d_circle, d_round_box), d_box)
    if operation_mode == 3:
        return smooth_union(smooth_union(d_circle, d_box, 54), d_round_box, 46)
    return sdf_union(sdf_union(d_circle, d_box), d_round_box)


def circle_sdf(x: float, y: float, radius: float) -> float:
    return math.hypot(x, y) - radius


def box_sdf(x: float, y: float, half_width: float, half_height: float) -> float:
    dx = abs(x) - half_width
    dy = abs(y) - half_height
    outside = math.hypot(max(dx, 0), max(dy, 0))
    inside = min(max(dx, dy), 0)
    return outside + inside


def rounded_box_sdf(x: float, y: float, half_width: float, half_height: float, radius: float) -> float:
    return box_sdf(x, y, half_width - radius, half_height - radius) - radius


def rotate_point(x: float, y: float, angle: float) -> tuple[float, float]:
    c = math.cos(angle)
    s = math.sin(angle)
    return x * c - y * s, x * s + y * c


def sdf_union(a: float, b: float) -> float:
    return min(a, b)


def sdf_intersection(a: float, b: float) -> float:
    return max(a, b)


def sdf_subtraction(a: float, b: float) -> float:
    return max(a, -b)


def smooth_union(a: float, b: float, radius: float) -> float:
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / radius))
    return (b * (1 - h) + a * h) - radius * h * (1 - h)


def draw_distance_field(distances: np.ndarray) -> None:
    rows, cols = distances.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            d = float(distances[row, col])
            if d < 0:
                hue = 198 + min(46, abs(d) * 0.32)
                saturation = 66
                brightness = 45 + min(48, abs(d) * 0.34)
            else:
                hue = 34 + min(38, d * 0.22)
                saturation = 38
                brightness = 98 - min(46, d * 0.28)
            py5.fill(hue, saturation, brightness, 100)
            py5.rect(col * PIXEL_STEP, row * PIXEL_STEP, PIXEL_STEP + 1, PIXEL_STEP + 1)


def draw_contour_lines(distances: np.ndarray) -> None:
    levels = [-90, -60, -30, 0, 30, 60, 90]
    for level in levels:
        if level == 0:
            py5.stroke(0, 0, 100, 96)
            py5.stroke_weight(2.4)
        else:
            py5.stroke(220 if level < 0 else 34, 24, 18, 40)
            py5.stroke_weight(1)
        draw_level_segments(distances, level)


def draw_level_segments(distances: np.ndarray, level: float) -> None:
    rows, cols = distances.shape
    for row in range(rows - 1):
        for col in range(cols - 1):
            x = col * PIXEL_STEP
            y = row * PIXEL_STEP
            corners = [
                (x, y, float(distances[row, col])),
                (x + PIXEL_STEP, y, float(distances[row, col + 1])),
                (x + PIXEL_STEP, y + PIXEL_STEP, float(distances[row + 1, col + 1])),
                (x, y + PIXEL_STEP, float(distances[row + 1, col])),
            ]
            crossings = cell_crossings(corners, level)
            if len(crossings) == 2:
                py5.line(crossings[0][0], crossings[0][1], crossings[1][0], crossings[1][1])
            elif len(crossings) == 4:
                py5.line(crossings[0][0], crossings[0][1], crossings[1][0], crossings[1][1])
                py5.line(crossings[2][0], crossings[2][1], crossings[3][0], crossings[3][1])


def cell_crossings(corners: list[tuple[float, float, float]], level: float) -> list[tuple[float, float]]:
    crossings = []
    for i in range(4):
        x1, y1, v1 = corners[i]
        x2, y2, v2 = corners[(i + 1) % 4]
        if (v1 >= level) == (v2 >= level):
            continue
        amount = 0.5 if abs(v2 - v1) < 1e-6 else (level - v1) / (v2 - v1)
        crossings.append((x1 + (x2 - x1) * amount, y1 + (y2 - y1) * amount))
    return crossings


def draw_info() -> None:
    mode_name = ["union", "intersection", "subtraction", "smooth union"][operation_mode]
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 570, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Signed distance field | {mode_name} | m: operation | c: contours | space: animate | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global operation_mode, show_contours, animate_shapes

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "signed_distance_field_####.png"))
    elif py5.key == "m":
        operation_mode = (operation_mode + 1) % 4
    elif py5.key == "c":
        show_contours = not show_contours
    elif py5.key == " ":
        animate_shapes = not animate_shapes


py5.run_sketch()
