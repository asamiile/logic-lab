from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

CELL_SIZE = 14
FIELD_MARGIN = CELL_SIZE * 2
THRESHOLD_STEP = 0.18

show_field = True
show_grid = False
animate_field = True
iso_mode = 0

field: np.ndarray | None = None


def setup() -> None:
    global field

    py5.size(700, 700)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    field = compute_field(0.0)


def draw() -> None:
    global field

    t = py5.frame_count * 0.018 if animate_field else 0.0
    field = compute_field(t)

    py5.background(218, 18, 96)
    if show_field:
        draw_field(field)
    if show_grid:
        draw_sampling_grid(field)
    draw_contours(field)
    draw_info()


def compute_field(t: float) -> np.ndarray:
    cols = int((py5.width - FIELD_MARGIN * 2) / CELL_SIZE) + 1
    rows = int((py5.height - FIELD_MARGIN * 2) / CELL_SIZE) + 1
    values = np.zeros((rows, cols), dtype=np.float32)

    centers = [
        (
            0.34 + 0.18 * math.cos(t * 1.17),
            0.42 + 0.16 * math.sin(t * 1.53),
            0.17,
            1.15,
        ),
        (
            0.65 + 0.14 * math.sin(t * 0.91 + 1.4),
            0.54 + 0.20 * math.cos(t * 1.31),
            0.21,
            1.0,
        ),
        (
            0.48 + 0.24 * math.cos(t * 0.67 + 2.1),
            0.25 + 0.10 * math.sin(t * 1.43),
            0.13,
            -0.7,
        ),
    ]

    for row in range(rows):
        y = row / max(1, rows - 1)
        for col in range(cols):
            x = col / max(1, cols - 1)
            v = 0.0
            for cx, cy, radius, strength in centers:
                dx = x - cx
                dy = y - cy
                v += strength * math.exp(-(dx * dx + dy * dy) / (2.0 * radius * radius))
            v += 0.22 * math.sin(10.5 * x + t * 1.7)
            v += 0.18 * math.cos(9.0 * y - t * 1.2)
            v += 0.12 * math.sin(7.0 * (x + y) + t * 0.8)
            values[row, col] = v

    min_value = float(values.min())
    max_value = float(values.max())
    return (values - min_value) / max(1e-6, max_value - min_value)


def draw_field(values: np.ndarray) -> None:
    rows, cols = values.shape
    py5.no_stroke()
    for row in range(rows - 1):
        for col in range(cols - 1):
            v = float(
                (
                    values[row, col]
                    + values[row, col + 1]
                    + values[row + 1, col]
                    + values[row + 1, col + 1]
                )
                * 0.25
            )
            hue = 202 + v * 118
            saturation = 34 + v * 52
            brightness = 98 - v * 42
            py5.fill(hue, saturation, brightness, 100)
            py5.rect(
                FIELD_MARGIN + col * CELL_SIZE,
                FIELD_MARGIN + row * CELL_SIZE,
                CELL_SIZE + 1,
                CELL_SIZE + 1,
            )


def draw_sampling_grid(values: np.ndarray) -> None:
    rows, cols = values.shape
    py5.stroke(0, 0, 15, 18)
    py5.stroke_weight(1)
    for row in range(rows):
        y = FIELD_MARGIN + row * CELL_SIZE
        py5.line(FIELD_MARGIN, y, FIELD_MARGIN + (cols - 1) * CELL_SIZE, y)
    for col in range(cols):
        x = FIELD_MARGIN + col * CELL_SIZE
        py5.line(x, FIELD_MARGIN, x, FIELD_MARGIN + (rows - 1) * CELL_SIZE)

    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            v = float(values[row, col])
            py5.fill(0, 0, 100 if v >= selected_thresholds()[0] else 8, 74)
            py5.circle(FIELD_MARGIN + col * CELL_SIZE, FIELD_MARGIN + row * CELL_SIZE, 3.5)


def draw_contours(values: np.ndarray) -> None:
    thresholds = selected_thresholds()
    for i, threshold in enumerate(thresholds):
        hue = (24 + i * 34) % 360
        py5.stroke(hue, 78, 96, 92)
        py5.stroke_weight(2.1 if iso_mode else 1.35)
        for segment in contour_segments(values, threshold):
            (x1, y1), (x2, y2) = segment
            py5.line(x1, y1, x2, y2)


def selected_thresholds() -> list[float]:
    if iso_mode == 1:
        return [0.5]
    if iso_mode == 2:
        return [0.35, 0.5, 0.65]
    return [round(v, 2) for v in np.arange(0.2, 0.82, THRESHOLD_STEP)]


def contour_segments(values: np.ndarray, threshold: float) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    rows, cols = values.shape
    segments = []
    for row in range(rows - 1):
        for col in range(cols - 1):
            x = FIELD_MARGIN + col * CELL_SIZE
            y = FIELD_MARGIN + row * CELL_SIZE
            corners = [
                (x, y, float(values[row, col])),
                (x + CELL_SIZE, y, float(values[row, col + 1])),
                (x + CELL_SIZE, y + CELL_SIZE, float(values[row + 1, col + 1])),
                (x, y + CELL_SIZE, float(values[row + 1, col])),
            ]
            crossings = cell_crossings(corners, threshold)
            if len(crossings) == 2:
                segments.append((crossings[0], crossings[1]))
            elif len(crossings) == 4:
                center_value = sum(corner[2] for corner in corners) * 0.25
                if center_value >= threshold:
                    segments.append((crossings[0], crossings[3]))
                    segments.append((crossings[1], crossings[2]))
                else:
                    segments.append((crossings[0], crossings[1]))
                    segments.append((crossings[2], crossings[3]))
    return segments


def cell_crossings(corners: list[tuple[float, float, float]], threshold: float) -> list[tuple[float, float]]:
    crossings = []
    for i in range(4):
        x1, y1, v1 = corners[i]
        x2, y2, v2 = corners[(i + 1) % 4]
        if (v1 >= threshold) == (v2 >= threshold):
            continue
        crossings.append(interpolate_point(x1, y1, v1, x2, y2, v2, threshold))
    return crossings


def interpolate_point(
    x1: float,
    y1: float,
    v1: float,
    x2: float,
    y2: float,
    v2: float,
    threshold: float,
) -> tuple[float, float]:
    if abs(v2 - v1) < 1e-6:
        return ((x1 + x2) * 0.5, (y1 + y2) * 0.5)
    amount = (threshold - v1) / (v2 - v1)
    return (x1 + (x2 - x1) * amount, y1 + (y2 - y1) * amount)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(0, 0, 10, 92)
    py5.rect(14, 14, 455, 48, 4)
    py5.fill(0, 0, 100, 100)
    mode_name = ["multi iso", "single iso", "three iso"][iso_mode]
    py5.text(
        f"Marching squares | {mode_name} | f: field | g: grid | m: mode | space: animate | s: save",
        24,
        43,
    )


def key_pressed() -> None:
    global show_field, show_grid, animate_field, iso_mode

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "marching_squares_####.png"))
    elif py5.key == "f":
        show_field = not show_field
    elif py5.key == "g":
        show_grid = not show_grid
    elif py5.key == "m":
        iso_mode = (iso_mode + 1) % 3
    elif py5.key == " ":
        animate_field = not animate_field


py5.run_sketch()
